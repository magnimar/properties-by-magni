from __future__ import annotations

import argparse
import logging
import time
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from bs4 import BeautifulSoup
from urllib.parse import urljoin

import base64
import os
import requests
import re

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv("/opt/properties-by-magni/.env")


def _configure_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


if not os.getenv("GOOGLE_MAPS_KEY"):
    raise RuntimeError(
        "CRITICAL: GOOGLE_MAPS_KEY is missing from environment. The scraper requires it to generate maps."
    )

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logging.error("DATABASE_URL not found in environment.")
    # We'll raise error only when trying to connect, to allow for local testing if needed.

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    min_bedrooms = Column(Integer, nullable=True)
    max_bedrooms = Column(Integer, nullable=True)
    min_size = Column(Float, default=0.0)
    max_size = Column(Float, default=1000.0)
    min_build_year = Column(Integer, nullable=True)
    max_build_year = Column(Integer, nullable=True)
    zip_codes = Column(String, nullable=True)
    ignored_streets = Column(String, nullable=True)
    einbylishus = Column(Boolean, default=False)
    fjolbylishus = Column(Boolean, default=False)
    atvinnuhusnaedi = Column(Boolean, default=False)
    radhus_parhus = Column(Boolean, default=False)
    sumarhus = Column(Boolean, default=False)
    parhus = Column(Boolean, default=False)
    jord_lod = Column(Boolean, default=False)
    haed = Column(Boolean, default=False)
    hesthus = Column(Boolean, default=False)
    oflokkad = Column(Boolean, default=False)
    outdoor_filter = Column(String, default="none")
    want_garage = Column(Boolean, default=False)
    scrape_hour = Column(Integer, default=20)
    ignored_properties = Column(String, nullable=True)


class ScraperRun(Base):
    __tablename__ = "scraper_runs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    fasteignanumer_list = Column(String, nullable=True)  # Comma separated list
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


def get_db_users() -> list[dict]:
    """Fetch verified users and their preferences from the database."""
    if not DATABASE_URL:
        logging.error("DATABASE_URL is missing. Cannot fetch users from DB.")
        return []

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_verified).all()
        user_configs = []
        for u in users:
            config = {
                "user_id": u.id,
                "user": u.email,
                "TO_EMAIL": u.email,
                "BREVO_API_KEY": os.getenv("BREVO_API_KEY"),
                "FROM_EMAIL": os.getenv("FROM_EMAIL"),
                "MIN_PRICE": int(u.min_price) if u.min_price is not None else 0,
                "MAX_PRICE": (
                    int(u.max_price) if u.max_price is not None else 1000000000
                ),
                "MIN_BEDROOMS": u.min_bedrooms if u.min_bedrooms is not None else 0,
                "MAX_BEDROOMS": u.max_bedrooms if u.max_bedrooms is not None else 10,
                "MIN_BUILD_YEAR": (
                    u.min_build_year if u.min_build_year is not None else 1900
                ),
                "MAX_BUILD_YEAR": (
                    u.max_build_year if u.max_build_year is not None else 2027
                ),
                "GOOGLE_MAPS_KEY": os.getenv("GOOGLE_MAPS_KEY"),
                "ZIP_CODES": u.zip_codes if u.zip_codes else "101,107",
                "outdoor_filter": u.outdoor_filter or "none",
                "want_garage": u.want_garage or False,
                "scrape_hour": u.scrape_hour if u.scrape_hour is not None else 20,
                "ignored_strings": (
                    u.ignored_streets.split(",") if u.ignored_streets else []
                ),
                "ignored_properties": (
                    u.ignored_properties.split(",") if u.ignored_properties else []
                ),
                "EINBYLISHUS": "yes" if u.einbylishus else "no",
                "FJOLBYLISHUS": "yes" if u.fjolbylishus else "no",
                "ATVINNUHUSNAEDI": "yes" if u.atvinnuhusnaedi else "no",
                "RADHUS_PARHUS": "yes" if u.radhus_parhus else "no",
                "SUMARHUS": "yes" if u.sumarhus else "no",
                "PARHUS": "yes" if u.parhus else "no",
                "JORD_LOD": "yes" if u.jord_lod else "no",
                "HAED": "yes" if u.haed else "no",
                "HESTHUS": "yes" if u.hesthus else "no",
                "OFLOKKAD": "yes" if u.oflokkad else "no",
            }
            user_configs.append(config)
        return user_configs
    finally:
        db.close()


def run_schedule_loop():
    """Check every minute and run Scraper for users whose scrape_hour matches current hour."""
    logging.info("Schedule mode: checking every minute for users to process.")

    # Track last run date per user: { "email@example.com": datetime.date }
    last_runs = {}

    while True:
        now = datetime.now()
        current_hour = now.hour
        current_date = now.date()

        user_configs = get_db_users()
        users_to_run = []

        for config in user_configs:
            email = config["user"]
            user_scrape_hour = config.get("scrape_hour", 20)

            if user_scrape_hour == current_hour:
                if last_runs.get(email) != current_date:
                    users_to_run.append(config)
                    last_runs[email] = current_date

        if users_to_run:
            logging.info(
                "Running scheduled batch for %d user(s) at %02d:00: %s",
                len(users_to_run),
                current_hour,
                ", ".join(c["user"] for c in users_to_run),
            )

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(_run_scraper_for_user, uc) for uc in users_to_run
                ]
                # We don't necessarily need to wait here if we want to be responsive,
                # but for simplicity and to avoid overlapping runs for the same user
                # in rare cases, we wait.
                for future in futures:
                    future.result()

        # Sleep until the start of the next minute
        time.sleep(60 - datetime.now().second)


def _run_scraper_for_user(user_config: dict):
    """Helper function to run the scraper for a single user and handle exceptions."""
    uid = user_config["user"]
    logging.info("Running scraper for %s...", uid)
    try:
        Scraper(user_config).main()
    except SystemExit as e:
        if e.code not in (0, None):
            logging.error(
                "Scraper exited with code %s for user %s",
                e.code,
                uid,
            )
    except Exception:
        logging.exception("Scraper failed for user %s", uid)


class Scraper:
    def __init__(self, user_config: dict):
        """user_config: one element from the database mapping (must include \"user\" and settings)."""
        self.user_config = user_config
        self.args = argparse.Namespace(user=user_config["user"])
        self.user_id = self.user_config.get("user_id")

        self.API_KEY = self.user_config.get("BREVO_API_KEY")
        self.FROM_EMAIL = self.user_config.get("FROM_EMAIL")
        self.TO_EMAIL = self.user_config.get("TO_EMAIL")
        self.MIN_PRICE = self.user_config.get("MIN_PRICE")
        self.MAX_PRICE = self.user_config.get("MAX_PRICE")
        self.MIN_BEDROOMS = self.user_config.get("MIN_BEDROOMS")
        self.MAX_BEDROOMS = self.user_config.get("MAX_BEDROOMS")
        self.MIN_SIZE = self.user_config.get("MIN_SIZE", 0)
        self.MAX_SIZE = self.user_config.get("MAX_SIZE", 1000000)
        self.MIN_BUILD_YEAR = self.user_config.get("MIN_BUILD_YEAR", 1900)
        self.MAX_BUILD_YEAR = self.user_config.get("MAX_BUILD_YEAR", 2027)
        self.GOOGLE_MAPS_KEY = self.user_config.get("GOOGLE_MAPS_KEY")
        self.ZIP_CODES = self.user_config.get("ZIP_CODES")
        self.OUTDOOR_FILTER = self.user_config.get("outdoor_filter", "none")
        self.WANT_GARAGE = self.user_config.get("want_garage", False)
        self.IGNORED_PROPERTIES = self.user_config.get("ignored_properties", [])
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip(
            "/"
        )
        self.BACKEND_URL = os.getenv("VITE_API_URL", "http://localhost:8000").rstrip(
            "/"
        )

        # Property categories
        categories = []
        if str(self.user_config.get("EINBYLISHUS", "")).lower() == "yes":
            categories.append("1")
        if str(self.user_config.get("FJOLBYLISHUS", "")).lower() == "yes":
            categories.append("2")
        if str(self.user_config.get("ATVINNUHUSNAEDI", "")).lower() == "yes":
            categories.append("3")
        if str(self.user_config.get("RADHUS_PARHUS", "")).lower() == "yes":
            categories.append("4")
        if str(self.user_config.get("SUMARHUS", "")).lower() == "yes":
            categories.append("6")
        if str(self.user_config.get("PARHUS", "")).lower() == "yes":
            categories.append("7")
        if str(self.user_config.get("JORD_LOD", "")).lower() == "yes":
            categories.append("8")
        if str(self.user_config.get("HAED", "")).lower() == "yes":
            categories.append("17")
        if str(self.user_config.get("HESTHUS", "")).lower() == "yes":
            categories.append("35")
        if str(self.user_config.get("OFLOKKAD", "")).lower() == "yes":
            categories.append("36")

        # If no categories specified, fallback to original default
        self.CATEGORIES = ",".join(categories) if categories else "2,1,4,7,17"

    def fetch_image_as_data_uri(self, image_url, referer=None, max_size_kb=500):
        """Fetch image from URL and return a data URI for embedding, or None on failure."""
        if not image_url or not image_url.startswith("http"):
            return None
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        }
        if referer:
            headers["Referer"] = referer
        try:
            r = requests.get(image_url, timeout=15, headers=headers)
            r.raise_for_status()
            content = r.content
            if len(content) > max_size_kb * 1024:
                return None
            content_type = (
                r.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
            )
            if content_type not in (
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
            ):
                content_type = "image/jpeg"
            b64 = base64.b64encode(content).decode("ascii")
            return f"data:{content_type};base64,{b64}"
        except Exception:
            return None

    def send_email_notification(self, subject, html_body):
        self.FROM_EMAIL = "fundvis@fundvis.is"

        if not all([self.API_KEY, self.FROM_EMAIL, self.TO_EMAIL]):
            logging.warning(
                "Email sending skipped due to missing API_KEY or TO_EMAIL in config/env."
            )
            return False

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = self.API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        sender = {"name": "Fundvís", "email": self.FROM_EMAIL}
        to = [{"email": self.TO_EMAIL}]

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to, html_content=html_body, sender=sender, subject=subject
        )

        logging.info(f"Attempting to send email to {self.TO_EMAIL}...")
        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            logging.info(
                f"Email sent successfully! Message ID: {api_response.message_id}"
            )
            return True
        except ApiException as e:
            logging.error(
                f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}"
            )
            return False

    NO_SEARCH_RESULTS_TEXT = "Leitin skilaði engum niðurstöðum."
    LISTING_AJAX_URL = "https://fasteignir.visir.is/ajaxsearch/getresults"

    def _search_listings_query_params(self, page: int) -> dict:
        """Query string for /ajaxsearch/getresults (same keys as the in-browser hash route)."""
        return {
            "stype": "sale",
            "zip": self.ZIP_CODES,
            "price": f"{self.MIN_PRICE},{self.MAX_PRICE}",
            "bedroom": f"{self.MIN_BEDROOMS},{self.MAX_BEDROOMS}",
            "category": self.CATEGORIES,
            "page": page,
        }

    def _parse_listing_cards_from_html(
        self, html: str, base_url: str, skip_address_substrings, processed_links: set
    ) -> tuple[list, int]:
        """Parse estate cards from HTML. Returns (new prop dicts, raw card count on page)."""
        soup = BeautifulSoup(html, "html.parser")
        property_cards = soup.find_all(
            "div", class_=lambda c: c and "estate__item" in c
        )
        raw_count = len(property_cards)
        out = []
        for card in property_cards:
            link_tag = card.find("a", class_="js-property-link", href=True)
            address_tag = card.find("div", class_="estate__item-title")
            price_tag = card.find("div", class_="estate__price")
            size_tag = card.find("div", class_="estate__parameters--1")
            rooms_tag = card.find("div", class_="estate__parameters--2")
            bedrooms_tag = card.find("div", class_="estate__parameters--4")

            image_tag = card.find("img")
            image_url = None
            if image_tag and image_tag.get("src"):
                image_url = urljoin(base_url, image_tag["src"])
            elif image_tag and image_tag.get("data-src"):
                image_url = urljoin(base_url, image_tag["data-src"])

            link = urljoin(base_url, link_tag["href"]) if link_tag else "N/A"
            address = (
                address_tag.get_text(strip=True, separator=" ")
                if address_tag
                else "N/A"
            )

            if re.search(r"\bseld\b", address, re.IGNORECASE):
                continue

            if any(
                substring.lower() in address.lower()
                for substring in skip_address_substrings
            ):
                continue

            price_str = price_tag.get_text(strip=True) if price_tag else "N/A"
            if price_str == "Tilboð":
                continue

            try:
                price_num = int(price_str.replace(".", "").replace(" kr", ""))
                if not int(self.MIN_PRICE) <= price_num <= int(self.MAX_PRICE):
                    continue
            except (ValueError, TypeError):
                continue

            size = size_tag.get_text(strip=True) if size_tag else "N/A"
            total_rooms = rooms_tag.get_text(strip=True) if rooms_tag else "N/A"
            bedrooms_text = bedrooms_tag.get_text(strip=True) if bedrooms_tag else "N/A"
            bedrooms = "1" if bedrooms_text == "N/A" else bedrooms_text

            open_house_tag = card.find(
                "div", class_=lambda c: c and "open-house" in c.lower()
            )
            open_house = open_house_tag.get_text(strip=True) if open_house_tag else None

            price_per_m2 = None
            if size != "N/A" and price_num:
                try:
                    size_num = float(size.replace("m²", "").replace(",", "."))
                    if size_num > 0:
                        price_per_m2 = int(price_num / size_num)
                except (ValueError, TypeError):
                    pass

            if link != "N/A" and address != "N/A":
                if link in processed_links:
                    continue
                processed_links.add(link)
                out.append(
                    {
                        "address": address,
                        "price": price_str,
                        "size_m2": size,
                        "price_per_m2": price_per_m2,
                        "total_rooms": total_rooms,
                        "bedrooms": bedrooms,
                        "link": link,
                        "image_url": image_url,
                        "open_house": open_house,
                    }
                )
        return out, raw_count

    def scrape_visir_properties(self):
        base_url = "https://fasteignir.visir.is"

        if not all(
            [
                self.MIN_PRICE is not None,
                self.MAX_PRICE is not None,
                self.MIN_BEDROOMS is not None,
                self.MAX_BEDROOMS is not None,
                self.ZIP_CODES,
            ]
        ):
            logging.error("Missing search parameters in config.")
            return [], None

        skip_address_substrings = self.user_config.get("ignored_strings", [])

        new_properties_found_this_run = []
        processed_links = set()

        headers = self._page_request_headers()
        headers["Referer"] = "https://fasteignir.visir.is/search/results/?stype=sale"

        page_num = 1
        max_pages = 500

        logging.info(
            "Fetching search pages via requests → %s (page=1, 2, … until no hits).",
            self.LISTING_AJAX_URL,
        )

        while page_num <= max_pages:
            try:
                response = requests.get(
                    self.LISTING_AJAX_URL,
                    params=self._search_listings_query_params(page_num),
                    headers=headers,
                    timeout=30,
                )
                response.raise_for_status()
                text = response.text
            except Exception as e:
                logging.error("Error fetching search page %s: %s", page_num, e)
                break

            if self.NO_SEARCH_RESULTS_TEXT in text:
                logging.info(
                    "Page %s: '%s' — stopping pagination.",
                    page_num,
                    self.NO_SEARCH_RESULTS_TEXT,
                )
                break

            added, raw_cards = self._parse_listing_cards_from_html(
                text, base_url, skip_address_substrings, processed_links
            )
            logging.info(
                "Page %s: %s card(s) on page, %s new after filters (running total %s).",
                page_num,
                raw_cards,
                len(added),
                len(processed_links),
            )

            if raw_cards == 0:
                logging.warning(
                    "Page %s: no listing cards in HTML and no empty-search message — stopping.",
                    page_num,
                )
                break

            new_properties_found_this_run.extend(added)
            page_num += 1
            time.sleep(0.5)

        return new_properties_found_this_run, None

    def get_numeric_price(self, price_str):
        try:
            return int(price_str.replace(".", "").replace(" kr", ""))
        except (ValueError, TypeError):
            return 0

    def _page_request_headers(self):
        """Same browser-like headers as image fetch (Referer set per-request)."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def check_property_details(self, prop):
        """Fetch property detail page with requests (balcony, terrace, image)."""
        if not prop.get("link"):
            return prop

        try:
            headers = self._page_request_headers()
            headers["Referer"] = "https://fasteignir.visir.is/"
            response = requests.get(prop["link"], timeout=15, headers=headers)
            response.raise_for_status()

            page_text = response.text.lower()
            soup = BeautifulSoup(response.text, "html.parser")

            if prop.get("has_balcony") is None:
                prop["has_balcony"] = "svalir" in page_text
            if prop.get("has_terrace") is None:
                prop["has_terrace"] = "sérafnota" in page_text or "garð" in page_text
            if prop.get("has_garage") is None:
                prop["has_garage"] = "bílskúr" in page_text

            if prop.get("build_year") is None:
                match = re.search(
                    r"bygg(?:t|ingará[\w]*?)[^\d]{0,20}(\d{4})", page_text
                )
                if match:
                    prop["build_year"] = match.group(1)
                else:
                    prop["build_year"] = "N/A"

            if prop.get("fasteignanumer") is None:
                fnum_elem = soup.find(string=re.compile("Fasteignanúmer", re.I))
                if (
                    fnum_elem
                    and fnum_elem.parent
                    and fnum_elem.parent.find_next_sibling()
                ):
                    prop["fasteignanumer"] = (
                        fnum_elem.parent.find_next_sibling().get_text(strip=True)
                    )
                else:
                    prop["fasteignanumer"] = "N/A"

            if prop.get("fasteignamat") is None:
                fmat_elem = soup.find(string=re.compile("Fasteignamat", re.I))
                if (
                    fmat_elem
                    and fmat_elem.parent
                    and fmat_elem.parent.find_next_sibling()
                ):
                    prop["fasteignamat"] = (
                        fmat_elem.parent.find_next_sibling().get_text(strip=True)
                    )
                else:
                    prop["fasteignamat"] = "N/A"

            # Extract contact information (tengiliður)
            if prop.get("contact_info") is None or prop.get("contact_info") == "N/A":
                # Try finding by the worker info container
                contact_section = soup.find("div", class_="details__worker-inner")
                if not contact_section:
                    # Fallback to the sidebar box structure
                    contact_section = soup.find("div", class_="details__slidebar-box")

                if contact_section:
                    name_elem = contact_section.find(
                        class_=re.compile(
                            r"agent-name|details__slidebar-title|agent__name"
                        )
                    )
                    name = name_elem.get_text(strip=True) if name_elem else "N/A"
                else:
                    # Final fallback for name if contact_section was not found
                    name_elem = soup.find(
                        class_=re.compile(
                            r"agent-name|details__slidebar-title|agent__name"
                        )
                    )
                    name = name_elem.get_text(strip=True) if name_elem else "N/A"

                search_context = contact_section if contact_section else soup

                # Company is often not explicitly labeled but might be in a link or text
                company_elem = soup.find("a", class_="details__slidebar-social-link")
                company = company_elem.get_text(strip=True) if company_elem else "N/A"

                phone_elem = search_context.find("a", href=re.compile(r"^tel:"))
                phone = phone_elem.get_text(strip=True) if phone_elem else "N/A"

                email_elem = search_context.find("a", href=re.compile(r"^mailto:"))
                email = email_elem.get_text(strip=True) if email_elem else "N/A"

                # Fallback: search the description for email and phone
                if email == "N/A" or phone == "N/A":
                    description_elem = soup.find(
                        class_=re.compile(
                            r"description__bottom-text|description-box|description"
                        )
                    )
                    text_to_search = (
                        description_elem.get_text(separator=" ")
                        if description_elem
                        else page_text
                    )

                    if email == "N/A":
                        email_match = re.search(
                            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
                            text_to_search,
                        )
                        if email_match:
                            email = email_match.group(0)

                    if phone == "N/A":
                        phone_match = re.search(r"\b\d{3}[- ]?\d{4}\b", text_to_search)
                        if phone_match:
                            phone = phone_match.group(0)

                if (
                    name != "N/A"
                    or company != "N/A"
                    or phone != "N/A"
                    or email != "N/A"
                ):
                    prop["contact_info"] = {
                        "name": name,
                        "company": company,
                        "phone": phone,
                        "email": email,
                    }
                else:
                    prop["contact_info"] = "N/A"

            if not prop.get("open_house") or prop.get("open_house").strip().lower() in [
                "opið hús",
                "opið hús:",
            ]:
                oh_elem = soup.find(string=re.compile("Opið hús", re.I))
                if oh_elem:
                    text = oh_elem.parent.get_text(strip=True, separator=" ")
                    if len(text) < 15 and oh_elem.parent.parent:
                        text = oh_elem.parent.parent.get_text(strip=True, separator=" ")
                    if (
                        len(text) < 15
                        and oh_elem.parent.parent
                        and oh_elem.parent.parent.find_next_sibling()
                    ):
                        text += (
                            " "
                            + oh_elem.parent.parent.find_next_sibling().get_text(
                                strip=True, separator=" "
                            )
                        )
                    prop["open_house"] = text if len(text) < 150 else text[:147]
                else:
                    prop["open_house"] = None

            if not prop.get("image_url") or "staticmap" in (
                prop.get("image_url") or ""
            ):
                img_tag = soup.find(
                    "img",
                    src=lambda s: s and "api-beta.fasteignir.is/pictures" in s,
                )
                if not img_tag:
                    for img in soup.find_all("img", attrs={"data-src": True}):
                        if img.get(
                            "data-src"
                        ) and "api-beta.fasteignir.is/pictures" in img.get(
                            "data-src", ""
                        ):
                            img_tag = img
                            break
                if img_tag:
                    image_url = img_tag.get("src") or img_tag.get("data-src")
                    if image_url:
                        if not image_url.startswith("http"):
                            image_url = urljoin(prop["link"], image_url)
                        prop["image_url"] = image_url

        except Exception as e:
            logging.warning(
                "Failed to check details for %s: %s", prop.get("address"), e
            )
            if prop.get("has_balcony") is None:
                prop["has_balcony"] = False
            if prop.get("has_terrace") is None:
                prop["has_terrace"] = False
            if prop.get("has_garage") is None:
                prop["has_garage"] = False
            if prop.get("build_year") is None:
                prop["build_year"] = "N/A"
            if prop.get("fasteignanumer") is None:
                prop["fasteignanumer"] = "N/A"
            if prop.get("fasteignamat") is None:
                prop["fasteignamat"] = "N/A"

        return prop

    @staticmethod
    def _get_location_names(zip_code: str) -> tuple[str, str]:
        """Returns (nominative_name, dative_name) for a given zip code."""
        locations = {
            "101": ("Reykjavík", "Reykjavík"),
            "102": ("Reykjavík", "Reykjavík"),
            "103": ("Reykjavík", "Reykjavík"),
            "104": ("Reykjavík", "Reykjavík"),
            "105": ("Reykjavík", "Reykjavík"),
            "107": ("Reykjavík", "Reykjavík"),
            "108": ("Reykjavík", "Reykjavík"),
            "109": ("Reykjavík", "Reykjavík"),
            "110": ("Reykjavík", "Reykjavík"),
            "111": ("Reykjavík", "Reykjavík"),
            "112": ("Reykjavík", "Reykjavík"),
            "113": ("Reykjavík", "Reykjavík"),
            "116": ("Reykjavík", "Reykjavík"),
            "161": ("Reykjavík", "Reykjavík"),
            "162": ("Reykjavík", "Reykjavík"),
            "200": ("Kópavogur", "Kópavogi"),
            "201": ("Kópavogur", "Kópavogi"),
            "202": ("Kópavogur", "Kópavogi"),
            "203": ("Kópavogur", "Kópavogi"),
            "206": ("Kópavogur", "Kópavogi"),
            "210": ("Garðabær", "Garðabæ"),
            "212": ("Garðabær", "Garðabæ"),
            "225": ("Garðabær", "Garðabæ"),
            "220": ("Hafnarfjörður", "Hafnarfirði"),
            "221": ("Hafnarfjörður", "Hafnarfirði"),
            "222": ("Hafnarfjörður", "Hafnarfirði"),
            "270": ("Mosfellsbær", "Mosfellsbæ"),
            "271": ("Mosfellsbær", "Mosfellsbæ"),
            "276": ("Mosfellsbær", "Mosfellsbæ"),
            "170": ("Seltjarnarnes", "Seltjarnarnesi"),
            "230": ("Keflavík", "Keflavík"),
            "232": ("Keflavík", "Keflavík"),
            "233": ("Hafnir", "Höfnum"),
            "262": ("Reykjanesbær", "Reykjanesbæ"),
            "240": ("Grindavík", "Grindavík"),
            "241": ("Grindavík", "Grindavík"),
            "245": ("Suðurnesjabær", "Suðurnesjabæ"),
            "246": ("Suðurnesjabær", "Suðurnesjabæ"),
            "250": ("Suðurnesjabær", "Suðurnesjabæ"),
            "251": ("Suðurnesjabær", "Suðurnesjabæ"),
            "260": ("Njarðvík", "Njarðvík"),
            "190": ("Vogar", "Vogum"),
            "191": ("Vogar", "Vogum"),
            "300": ("Akranes", "Akranesi"),
            "301": ("Akranes", "Akranesi"),
            "310": ("Borgarnes", "Borgarnesi"),
            "311": ("Borgarnes", "Borgarnesi"),
            "320": ("Reykholt", "Reykholti"),
            "340": ("Stykkishólmur", "Stykkishólmi"),
            "345": ("Flatey", "Flatey"),
            "350": ("Grundarfjörður", "Grundarfirði"),
            "355": ("Ólafsvík", "Ólafsvík"),
            "356": ("Snæfellsbær", "Snæfellsbæ"),
            "360": ("Hellissandur", "Hellissandi"),
            "370": ("Búðardalur", "Búðardal"),
            "371": ("Búðardalur", "Búðardal"),
            "380": ("Reykhólahreppur", "Reykhólahreppi"),
            "400": ("Ísafjörður", "Ísafirði"),
            "401": ("Ísafjörður", "Ísafirði"),
            "410": ("Hnífsdalur", "Hnífsdal"),
            "415": ("Bolungarvík", "Bolungarvík"),
            "416": ("Bolungarvík", "Bolungarvík"),
            "420": ("Súðavík", "Súðavík"),
            "421": ("Súðavík", "Súðavík"),
            "425": ("Flateyri", "Flateyri"),
            "426": ("Flateyri", "Flateyri"),
            "430": ("Suðureyri", "Suðureyri"),
            "431": ("Suðureyri", "Suðureyri"),
            "450": ("Patreksfjörður", "Patreksfirði"),
            "451": ("Patreksfjörður", "Patreksfirði"),
            "460": ("Tálknafjörður", "Tálknafirði"),
            "461": ("Tálknafjörður", "Tálknafirði"),
            "465": ("Bíldudalur", "Bíldudal"),
            "466": ("Bíldudalur", "Bíldudal"),
            "470": ("Þingeyri", "Þingeyri"),
            "471": ("Þingeyri", "Þingeyri"),
            "500": ("Staður", "Stað"),
            "510": ("Hólmavík", "Hólmavík"),
            "511": ("Hólmavík", "Hólmavík"),
            "512": ("Hólmavík", "Hólmavík"),
            "520": ("Drangsnes", "Drangsnesi"),
            "522": ("Kjörvogur", "Kjörvogi"),
            "523": ("Bær", "Bæ"),
            "524": ("Norðurfjörður", "Norðurfirði"),
            "530": ("Hvammstangi", "Hvammstanga"),
            "531": ("Hvammstangi", "Hvammstanga"),
            "540": ("Blönduós", "Blönduósi"),
            "541": ("Blönduós", "Blönduósi"),
            "545": ("Skagaströnd", "Skagaströnd"),
            "546": ("Skagaströnd", "Skagaströnd"),
            "550": ("Sauðárkrókur", "Sauðárkróki"),
            "551": ("Sauðárkrókur", "Sauðárkróki"),
            "560": ("Varmahlíð", "Varmahlíð"),
            "561": ("Varmahlíð", "Varmahlíð"),
            "565": ("Hofsós", "Hofsósi"),
            "566": ("Hofsós", "Hofsósi"),
            "570": ("Fljót", "Fljótum"),
            "580": ("Siglufjörður", "Siglufirði"),
            "581": ("Siglufjörður", "Siglufirði"),
            "600": ("Akureyri", "Akureyri"),
            "601": ("Akureyri", "Akureyri"),
            "602": ("Akureyri", "Akureyri"),
            "603": ("Akureyri", "Akureyri"),
            "604": ("Akureyri", "Akureyri"),
            "605": ("Akureyri", "Akureyri"),
            "606": ("Akureyri", "Akureyri"),
            "607": ("Akureyri", "Akureyri"),
            "610": ("Árskógssandur", "Árskógssandi"),
            "611": ("Grímsey", "Grímsey"),
            "616": ("Grenivík", "Grenivík"),
            "620": ("Dalvík", "Dalvík"),
            "621": ("Dalvík", "Dalvík"),
            "625": ("Ólafsfjörður", "Ólafsfirði"),
            "626": ("Ólafsfjörður", "Ólafsfirði"),
            "630": ("Hrísey", "Hrísey"),
            "640": ("Húsavík", "Húsavík"),
            "641": ("Húsavík", "Húsavík"),
            "645": ("Fosshóll", "Fosshóli"),
            "650": ("Laugar", "Laugum"),
            "660": ("Mývatn", "Mývatni"),
            "670": ("Kópasker", "Kópaskeri"),
            "671": ("Kópasker", "Kópaskeri"),
            "675": ("Raufarhöfn", "Raufarhöfn"),
            "680": ("Þórshöfn", "Þórshöfn"),
            "681": ("Þórshöfn", "Þórshöfn"),
            "700": ("Egilsstaðir", "Egilsstöðum"),
            "701": ("Egilsstaðir", "Egilsstöðum"),
            "710": ("Seyðisfjörður", "Seyðisfirði"),
            "715": ("Mjóifjörður", "Mjóafirði"),
            "720": ("Borgarfjörður eystri", "Borgarfirði eystra"),
            "730": ("Reyðarfjörður", "Reyðarfirði"),
            "735": ("Eskifjörður", "Eskifirði"),
            "740": ("Neskaupstaður", "Neskaupstað"),
            "750": ("Fáskrúðsfjörður", "Fáskrúðsfirði"),
            "755": ("Stöðvarfjörður", "Stöðvarfirði"),
            "760": ("Breiðdalsvík", "Breiðdalsvík"),
            "765": ("Djúpivogur", "Djúpavogi"),
            "780": ("Höfn í Hornafirði", "Höfn í Hornafirði"),
            "781": ("Höfn í Hornafirði", "Höfn í Hornafirði"),
            "785": ("Öræfi", "Öræfum"),
            "800": ("Selfoss", "Selfossi"),
            "801": ("Selfoss", "Selfossi"),
            "802": ("Selfoss", "Selfossi"),
            "803": ("Selfoss", "Selfossi"),
            "804": ("Selfoss", "Selfossi"),
            "805": ("Selfoss", "Selfossi"),
            "806": ("Selfoss", "Selfossi"),
            "810": ("Hveragerði", "Hveragerði"),
            "815": ("Þorlákshöfn", "Þorlákshöfn"),
            "816": ("Ölfus", "Ölfusi"),
            "820": ("Eyrarbakki", "Eyrarbakka"),
            "825": ("Stokkseyri", "Stokkseyri"),
            "840": ("Laugarvatn", "Laugarvatni"),
            "845": ("Flúðir", "Flúðum"),
            "846": ("Flúðir", "Flúðum"),
            "850": ("Hella", "Hellu"),
            "851": ("Hella", "Hellu"),
            "860": ("Hvolsvöllur", "Hvolsvelli"),
            "861": ("Hvolsvöllur", "Hvolsvelli"),
            "870": ("Vík", "Vík"),
            "871": ("Vík", "Vík"),
            "880": ("Kirkjubæjarklaustur", "Kirkjubæjarklaustri"),
            "881": ("Kirkjubæjarklaustur", "Kirkjubæjarklaustri"),
            "900": ("Vestmannaeyjar", "Vestmannaeyjum"),
            "901": ("Vestmannaeyjabær", "Vestmannaeyjabæ"),
            "950": ("Útlönd", "Útlöndum"),
            "951": ("Útlönd", "Útlöndum"),
            "952": ("Útlönd", "Útlöndum"),
            "953": ("Útlönd", "Útlöndum"),
            "954": ("Útlönd", "Útlöndum"),
            "955": ("Útlönd", "Útlöndum"),
            "956": ("Útlönd", "Útlöndum"),
            "970": ("Útlönd", "Útlöndum"),
            "971": ("Útlönd", "Útlöndum"),
            "980": ("Útlönd", "Útlöndum"),
            "999": ("Útlönd", "Útlöndum"),
        }
        return locations.get(zip_code, ("", ""))

    def get_email_template(self, content, title="Fundvís"):
        from premailer import transform

        html = f"""
        <!DOCTYPE html>
        <html lang="is">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="format-detection" content="telephone=no, date=no, address=no, email=no">
            <title>{title}</title>
        </head>
        <body>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #334155;
                    background-color: #f8fafc;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 650px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                }}
                .header {{
                    background-color: #1e293b;
                    padding: 30px;
                    text-align: center;
                    color: #ffffff;
                }}
                .header img {{
                    max-width: 150px;
                    height: auto;
                    margin-bottom: 10px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                    letter-spacing: -0.025em;
                }}
                .content {{
                    padding: 30px;
                }}
                .stats-box {{
                    background-color: #f1f5f9;
                    border-radius: 6px;
                    padding: 20px;
                    margin-bottom: 30px;
                }}
                .property-card {{
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    overflow: hidden;
                    background-color: #ffffff;
                }}
                .property-image {{
                    width: 100%;
                    max-height: 400px;
                    object-fit: cover;
                    display: block;
                }}
                .property-info {{
                    padding: 20px;
                }}
                .property-title {{
                    font-size: 20px;
                    font-weight: 700;
                    color: #1e293b;
                    margin: 0 0 10px 0;
                }}
                .property-price {{
                    font-size: 18px;
                    color: #2563eb;
                    font-weight: 600;
                    margin-bottom: 15px;
                }}
                .property-details {{
                    font-size: 14px;
                    margin-bottom: 20px;
                    overflow: hidden;
                }}
                .detail-item {{
                    width: 48%;
                    float: left;
                    margin-bottom: 5px;
                }}
                .detail-label {{
                    font-weight: 600;
                    color: #64748b;
                    margin-right: 5px;
                }}
                .footer {{
                    background-color: #f1f5f9;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #64748b;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #2563eb;
                    color: #ffffff !important;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    text-align: center;
                    margin-bottom: 10px;
                }}
                .button-danger {{
                    display: inline-block;
                    padding: 8px 16px;
                    background-color: #ef4444;
                    color: #ffffff !important;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 12px;
                    text-align: center;
                    margin-bottom: 10px;
                }}
                .button:hover {{
                    background-color: #1d4ed8;
                }}
                h2, h3 {{
                    color: #1e293b;
                }}
                hr {{
                    border: 0;
                    border-top: 1px solid #e2e8f0;
                    margin: 30px 0;
                }}
                /* Prevent auto-styling of links for dates/addresses */
                a[x-apple-data-detectors],
                .x-gmail-data-detectors,
                .x-gmail-data-detectors *,
                .aBn {{
                    color: inherit !important;
                    text-decoration: none !important;
                    font-size: inherit !important;
                    font-family: inherit !important;
                    font-weight: inherit !important;
                    line-height: inherit !important;
                }}
                .open-house-text a {{
                    color: #ffffff !important;
                    text-decoration: none !important;
                }}
                @media only screen and (max-width: 600px) {{
                    .container {{
                        margin: 0 !important;
                        width: 100% !important;
                        max-width: 100% !important;
                        border-radius: 0 !important;
                    }}
                    .content {{
                        padding: 20px !important;
                    }}
                    .header {{
                        padding: 25px 20px !important;
                    }}
                    .header h1 {{
                        font-size: 20px !important;
                    }}
                    .detail-item {{
                        width: 100% !important;
                        float: none !important;
                    }}
                    .property-title {{
                        font-size: 18px !important;
                    }}
                    .property-image {{
                        max-height: 250px !important;
                    }}
                    .button, .button-danger {{
                        display: block !important;
                        width: 100% !important;
                        box-sizing: border-box;
                    }}
                }}
            </style>
            <div class="container">
                <div class="header">
                    <h1>Fundvís</h1>
                </div>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    &copy; 2026 Fundvís. Allt rétt áskilinn.<br>
                    Þú færð þennan tölvupóst því þú ert skráð(ur) á vakt hjá okkur.
                </div>
            </div>
        </body>
        </html>
        """
        return transform(html)

    def create_google_calendar_link(self, address, open_house_text):
        if not open_house_text or open_house_text.strip() == "":
            return None

        import re
        import urllib.parse
        import datetime

        dates = re.findall(
            r"(\d{1,2}\.\s*[a-zA-ZáéíóúýþæöÁÉÍÓÚÝÞÆÖ]+(?:\s*\d{4})?)", open_house_text
        )
        times = re.findall(r"(\d{2}:\d{2})", open_house_text)

        if dates and len(times) >= 1:
            date_str = dates[0]
            start_time = times[0]

            # If there's an end time, use it, else default to 30 mins later
            if len(times) >= 2:
                end_time = times[1]
            else:
                h, m = map(int, start_time.split(":"))
                m += 30
                if m >= 60:
                    m -= 60
                    h += 1
                end_time = f"{h:02d}:{m:02d}"

            months = {
                "janúar": "01",
                "jan": "01",
                "febrúar": "02",
                "feb": "02",
                "mars": "03",
                "mar": "03",
                "apríl": "04",
                "apr": "04",
                "maí": "05",
                "mai": "05",
                "júní": "06",
                "jun": "06",
                "júlí": "07",
                "jul": "07",
                "ágúst": "08",
                "agu": "08",
                "september": "09",
                "sep": "09",
                "október": "10",
                "okt": "10",
                "nóvember": "11",
                "nov": "11",
                "desember": "12",
                "des": "12",
            }

            day_match = re.search(r"(\d{1,2})", date_str)
            if not day_match:
                return None
            day = day_match.group(1).zfill(2)

            month_match = re.search(r"([a-zA-ZáéíóúýþæöÁÉÍÓÚÝÞÆÖ]+)", date_str)
            if not month_match:
                return None
            month_word = month_match.group(1).lower()

            month = "01"
            for k, v in months.items():
                if month_word.startswith(k) or k.startswith(month_word):
                    month = v
                    break

            current_year = datetime.datetime.now().year
            year_match = re.search(r"(\d{4})", date_str)
            year = year_match.group(1) if year_match else str(current_year)

            start_dt = f"{year}{month}{day}T{start_time.replace(':', '')}00"
            end_dt = f"{year}{month}{day}T{end_time.replace(':', '')}00"

            base = "https://calendar.google.com/calendar/render?action=TEMPLATE"
            title = urllib.parse.quote(f"Opið hús: {address}")
            dates_param = f"{start_dt}/{end_dt}"
            loc = urllib.parse.quote(address)

            return f"{base}&text={title}&dates={dates_param}&location={loc}"

        return None

    def generate_property_html(self, properties, title):
        html = f"<h2 style='border-bottom: 2px solid #2563eb; padding-bottom: 10px;'>{title}</h2>"
        for prop in properties:
            html += "<div class='property-card'>"
            if prop.get("image_url"):
                html += f"<img src='{prop['image_url']}' alt='{prop['address']}' class='property-image' />"
            if prop.get("open_house"):
                cal_link = self.create_google_calendar_link(
                    prop.get("address", "Fasteign"), prop["open_house"]
                )
                oh_safe = "".join(
                    [c + "&#8203;" if c.isdigit() else c for c in prop["open_house"]]
                )
                if cal_link:
                    html += f"<table width='100%' cellpadding='0' cellspacing='0' border='0' style='background-color: #1d4ed8; color: white;'><tr><td style='padding: 12px 10px 12px 20px; font-weight: 800; font-size: 1.1em; text-align: left; vertical-align: middle;' class='open-house-text'><span style='color: #ffffff !important; text-decoration: none !important;'>{oh_safe}</span></td><td style='padding: 12px 20px 12px 10px; text-align: right; vertical-align: middle;' width='1%'><a href='{cal_link}' target='_blank' style='display: inline-block; background-color: #ffffff; color: #1d4ed8; padding: 6px 12px; border-radius: 4px; font-size: 12px; text-decoration: none; font-weight: bold; white-space: nowrap;'>Bæta í dagatal</a></td></tr></table>"
                else:
                    html += f"<div style='background-color: #1d4ed8; color: white; padding: 12px; font-weight: 800; text-align: center; font-size: 1.1em;' class='open-house-text'><span style='color: #ffffff !important; text-decoration: none !important;'>{oh_safe}</span></div>"

            html += "<div class='property-info'>"
            html += f"<h3 class='property-title'>{prop['address']}</h3>"
            html += f"<div class='property-price'>{prop['price']}</div>"

            html += "<div class='property-details'>"
            if prop.get("fasteignamat") and prop["fasteignamat"] != "N/A":
                html += f"<div class='detail-item'><span class='detail-label'>Fasteignamat:</span> {prop['fasteignamat']}</div>"

            html += f"<div class='detail-item'><span class='detail-label'>Stærð:</span> {prop['size_m2']}</div>"
            html += f"<div class='detail-item'><span class='detail-label'>Svefnherbergi:</span> {prop['bedrooms']}</div>"

            if prop.get("price_per_m2"):
                price_per_m2_formatted = f"{prop['price_per_m2']:,}".replace(",", ".")
                html += f"<div class='detail-item'><span class='detail-label'>Fermetraverð:</span> {price_per_m2_formatted} kr.</div>"

            if prop.get("build_year") and prop["build_year"] != "N/A":
                html += f"<div class='detail-item'><span class='detail-label'>Byggt:</span> {prop['build_year']}</div>"

            outdoor = []
            if prop.get("has_balcony"):
                outdoor.append("Svalir")
            if prop.get("has_terrace"):
                outdoor.append("Garður")
            if outdoor:
                html += f"<div class='detail-item'><span class='detail-label'>Útisvæði:</span> {', '.join(outdoor)}</div>"

            if prop.get("has_garage"):
                html += "<div class='detail-item'><span class='detail-label'>Bílskúr:</span> Já</div>"

            html += "</div>"  # end property-details

            # Google Map
            if self.GOOGLE_MAPS_KEY:
                import urllib.parse

                map_addr = f"{prop['address']}, Iceland"
                map_addr_encoded = urllib.parse.quote(map_addr)
                static_map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={map_addr_encoded}&zoom=15&size=600x200&scale=2&maptype=roadmap&markers=color:red%7C{map_addr_encoded}&key={self.GOOGLE_MAPS_KEY}"
                gmaps_url = f"https://www.google.com/maps/search/?api=1&query={map_addr_encoded}"
                html += f"<div style='margin-bottom: 20px; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;'><a href='{gmaps_url}' target='_blank'><img src='{static_map_url}' alt='Map' style='width: 100%; height: auto; display: block;' /></a></div>"

            try:
                numeric_price = int(prop["price"].replace(".", "").replace(" kr", ""))
                loan_70 = numeric_price * 0.70
                loan_10 = numeric_price * 0.10
                loan_80 = numeric_price * 0.80

                interest_payment = int(
                    (loan_70 * 0.007116666666666666) + (loan_10 * 0.007708333333333334)
                )
                principal_payment = int(loan_80 * 0.00023890801001251563)
                monthly_payment = interest_payment + principal_payment
                monthly_formatted = f"{monthly_payment:,}".replace(",", ".")

                html += f"<p style='font-size: 13px; color: #64748b; margin-top: 0;'><strong>Áætluð afborgun:</strong> {monthly_formatted} kr./mán (80% lán, óverðtryggt)</p>"
            except (ValueError, TypeError, KeyError):
                pass

            if prop.get("contact_info") and isinstance(prop["contact_info"], dict):
                c = prop["contact_info"]
                html += f"""
                <div style='margin-top: 20px; padding-top: 15px; border-top: 1px solid #e2e8f0;'>
                    <p style='font-size: 13px; color: #64748b; margin: 0 0 5px 0;'><strong>Tengiliður:</strong></p>
                    <p style='font-size: 14px; font-weight: 600; color: #1e293b; margin: 0;'>{c['name']}</p>
                    {f"<p style='font-size: 13px; color: #64748b; margin: 2px 0;'>{c['company']}</p>" if c.get('company') and c['company'] != 'N/A' else ''}
                    <p style='font-size: 13px; margin: 5px 0 0 0;'>
                        {f"<a href='tel:{c['phone']}' style='color: #2563eb; text-decoration: none;'>{c['phone']}</a>" if c.get('phone') and c['phone'] != 'N/A' else ''}
                        {f" &nbsp;|&nbsp; <a href='mailto:{c['email']}' style='color: #2563eb; text-decoration: none;'>{c['email']}</a>" if c.get('email') and c['email'] != 'N/A' else ''}
                    </p>
                </div>
                """

            html += "<div style='margin-top: 15px; text-align: center;'>"
            html += f"  <a href='{prop['link']}' class='button'>Skoða eign á Vísi</a>"
            if prop.get("fasteignanumer") and prop["fasteignanumer"] != "N/A":
                ignore_link = f"{self.BACKEND_URL}/ignore-property-public?email={self.TO_EMAIL}&fasteignanumer={prop['fasteignanumer']}"
                html += f"  <a href='{ignore_link}' class='button-danger'>Ég vil ekki sjá þessa eign aftur</a>"
            html += "</div>"
            html += "</div></div>"  # end property-info and property-card
        return html

    def print_properties(self, properties, title):
        logging.info(f"\n--- {title} ---")
        for i, prop in enumerate(properties):
            logging.info(f"\nProperty #{i + 1}")
            logging.info(f"  Address: {prop['address']}")
            logging.info(f"  Price: {prop['price']}")
            if prop.get("fasteignamat") and prop["fasteignamat"] != "N/A":
                logging.info(f"  Fasteignamat: {prop['fasteignamat']}")
            logging.info(f"  Size: {prop['size_m2']}")
            if prop.get("price_per_m2"):
                price_per_m2_formatted = f"{prop['price_per_m2']:,}".replace(",", ".")
                logging.info(f"  Price per m²: {price_per_m2_formatted} kr.")
            logging.info(f"  Bedrooms: {prop['bedrooms']}")

            try:
                numeric_price = int(prop["price"].replace(".", "").replace(" kr", ""))
                loan_70 = numeric_price * 0.70
                loan_10 = numeric_price * 0.10
                loan_80 = numeric_price * 0.80

                interest_payment = int(
                    (loan_70 * 0.007116666666666666) + (loan_10 * 0.007708333333333334)
                )
                principal_payment = int(loan_80 * 0.00023890801001251563)
                monthly_payment = interest_payment + principal_payment
                monthly_formatted = f"{monthly_payment:,}".replace(",", ".")
                principal_formatted = f"{principal_payment:,}".replace(",", ".")

                logging.info(
                    f"  Monthly Payment (Non-indexed, 40 yrs, 80% loan): {monthly_formatted} kr."
                )
                logging.info(f"  Principal Paid Down: {principal_formatted} kr.")
            except (ValueError, TypeError, KeyError):
                pass

            if prop.get("build_year") and prop["build_year"] != "N/A":
                logging.info(f"  Built: {prop['build_year']}")
            if prop.get("contact_info") and isinstance(prop["contact_info"], dict):
                c = prop["contact_info"]
                logging.info(
                    f"  Contact: {c['name']} ({c['company']}) - {c['phone']} / {c['email']}"
                )
            if prop.get("has_balcony") is not None:
                logging.info(f"  Balcony: {'yes' if prop['has_balcony'] else 'no'}")
            if prop.get("has_terrace") is not None:
                logging.info(f"  Terrace: {'yes' if prop['has_terrace'] else 'no'}")
            if prop.get("has_garage") is not None:
                logging.info(f"  Garage: {'yes' if prop['has_garage'] else 'no'}")
            logging.info(f"  Link: {prop['link']}")

    def main(self):
        logging.info(f"Scraper main start for {self.user_config['user']}")
        new_properties, _ = self.scrape_visir_properties()

        def needs_detail_check(prop):
            return (
                prop.get("has_balcony") is None
                or prop.get("has_terrace") is None
                or prop.get("has_garage") is None
                or prop.get("build_year") is None
                or prop.get("fasteignamat") is None
                or prop.get("contact_info") is None
                or prop.get("contact_info") == "N/A"
                or not prop.get("open_house")
                or prop.get("open_house").strip().lower() in ["opið hús", "opið hús:"]
                or not prop.get("image_url")
                or "staticmap" in (prop.get("image_url") or "")
            )

        to_check = [p for p in new_properties if needs_detail_check(p)]
        logging.info(
            "Checking %d / %d properties in parallel...",
            len(to_check),
            len(new_properties),
        )
        if to_check:
            with ThreadPoolExecutor(max_workers=15) as executor:
                list(executor.map(self.check_property_details, to_check))

        new_properties.sort(key=lambda x: self.get_numeric_price(x["price"]))

        # Filter based on outdoor preferences, garage and build year
        filtered_properties = []
        for prop in new_properties:
            if prop.get("fasteignanumer") in self.IGNORED_PROPERTIES:
                continue
            if self.WANT_GARAGE and not prop.get("has_garage"):
                continue

            # Build year filtering
            try:
                b_year = prop.get("build_year")
                if b_year and b_year != "N/A":
                    build_year_int = int(b_year)
                    if (
                        build_year_int < self.MIN_BUILD_YEAR
                        or build_year_int > self.MAX_BUILD_YEAR
                    ):
                        continue
            except (ValueError, TypeError):
                pass

            # Size filtering
            try:
                size_str = prop.get("size_m2")
                if size_str and size_str != "N/A":
                    # Remove 'm²', replace ',' with '.' and convert to float
                    size_num = float(
                        size_str.replace("m²", "").replace(",", ".").strip()
                    )
                    if size_num < self.MIN_SIZE or size_num > self.MAX_SIZE:
                        continue
            except (ValueError, TypeError):
                pass

            if self.OUTDOOR_FILTER == "balcony":
                if not prop.get("has_balcony"):
                    continue
            elif self.OUTDOOR_FILTER == "garden":
                if not prop.get("has_terrace"):
                    continue
            elif self.OUTDOOR_FILTER == "either":
                if not (prop.get("has_balcony") or prop.get("has_terrace")):
                    continue
            elif self.OUTDOOR_FILTER == "both":
                if not (prop.get("has_balcony") and prop.get("has_terrace")):
                    continue
            filtered_properties.append(prop)

        new_properties = filtered_properties
        logging.info(
            f"Found {len(new_properties)} properties matching outdoor/garage filters."
        )

        # Fetch the last run's fasteignanumer for this user to identify new properties
        last_run_fasteignanumer = []
        if self.user_id and DATABASE_URL:
            engine = create_engine(DATABASE_URL)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            try:
                last_run = (
                    db.query(ScraperRun)
                    .filter(ScraperRun.user_id == self.user_id)
                    .order_by(ScraperRun.created_at.desc())
                    .first()
                )
                if last_run and last_run.fasteignanumer_list:
                    last_run_fasteignanumer = last_run.fasteignanumer_list.split(",")
                
                # Now save current run fasteignanumer
                current_fasteignanumer_list = [
                    p.get("fasteignanumer") for p in new_properties if p.get("fasteignanumer")
                ]
                if current_fasteignanumer_list:
                    new_run = ScraperRun(
                        user_id=self.user_id,
                        fasteignanumer_list=",".join(current_fasteignanumer_list),
                    )
                    db.add(new_run)
                    db.commit()
                    logging.info(f"Saved {len(current_fasteignanumer_list)} properties to ScraperRun for user {self.user_id}")
            except Exception as e:
                logging.error(f"Failed to fetch or save ScraperRun: {e}")
            finally:
                db.close()

        # Identify properties that were NOT in the last run
        new_since_last_run = []
        if last_run_fasteignanumer: # Only show this if there was a previous run
            for prop in new_properties:
                fnum = prop.get("fasteignanumer")
                if fnum and fnum not in last_run_fasteignanumer:
                    new_since_last_run.append(prop)

        deal_of_the_day = None
        best_ratio = float("inf")
        for prop in new_properties:
            price_val = self.get_numeric_price(prop.get("price", ""))
            fmat_val = self.get_numeric_price(prop.get("fasteignamat", ""))
            if price_val > 0 and fmat_val > 0:
                ratio = price_val / fmat_val
                if ratio < best_ratio:
                    best_ratio = ratio
                    deal_of_the_day = prop

        if deal_of_the_day:
            logging.info(f"Deal of the day found: {deal_of_the_day['address']}")

        allowed_zips = [
            z.strip() for z in (self.ZIP_CODES or "").split(",") if z.strip()
        ]
        random.shuffle(allowed_zips)

        properties_by_zip = {}
        for prop in new_properties:
            zip_code = "Annað"
            matches = list(re.finditer(r"(?<!\d)\d{3}(?!\d)", prop["address"]))
            for match in reversed(matches):
                val = match.group()
                if val in allowed_zips:
                    zip_code = val
                    start = match.start()
                    prefix = prop["address"][:start].rstrip()
                    if not prefix.endswith(","):
                        prop["address"] = prefix + ", " + prop["address"][start:]
                    break
            properties_by_zip.setdefault(zip_code, []).append(prop)

        for zip_code, props in properties_by_zip.items():
            random.shuffle(props)
            base_name, dative_name = self._get_location_names(zip_code)
            if base_name:
                title = f"Fasteignir í {zip_code} {dative_name}"
            elif zip_code != "Annað":
                title = f"Fasteignir í {zip_code}"
            else:
                title = "Fasteignir (óþekkt póstnúmer)"
            self.print_properties(props, title)

        if new_properties:
            subject = f"Fann {len(new_properties)} eignir fyrir þig"

            stats_html = "<div class='stats-box'>"
            stats_html += "<h3>Meðalfermetraverð eftir hverfi:</h3><ul>"

            # --- Average Price Statistics ---
            avg_price_per_m2 = {}
            bedroom_counts = {}
            for prop in new_properties:
                bedrooms = prop.get("bedrooms", "N/A")
                if bedrooms not in avg_price_per_m2:
                    avg_price_per_m2[bedrooms] = 0
                    bedroom_counts[bedrooms] = 0
                if prop.get("price_per_m2"):
                    avg_price_per_m2[bedrooms] += prop["price_per_m2"]
                    bedroom_counts[bedrooms] += 1
            for bedrooms, total_price in avg_price_per_m2.items():
                if bedroom_counts[bedrooms] > 0:
                    avg_price_per_m2[bedrooms] = int(
                        total_price / bedroom_counts[bedrooms]
                    )

            sorted_zips = sorted(
                allowed_zips, key=lambda x: int(x) if x.isdigit() else x
            )
            for zip_code in sorted_zips + ["Annað"]:
                if zip_code in properties_by_zip:
                    zip_props = properties_by_zip[zip_code]
                    zip_total_m2_price = sum(
                        p.get("price_per_m2", 0)
                        for p in zip_props
                        if p.get("price_per_m2")
                    )
                    zip_props_with_m2 = sum(
                        1 for p in zip_props if p.get("price_per_m2")
                    )
                    if zip_props_with_m2 > 0:
                        zip_avg_m2 = int(zip_total_m2_price / zip_props_with_m2)
                        zip_avg_m2_formatted = f"{zip_avg_m2:,}".replace(",", ".")
                        base_name, _ = self._get_location_names(zip_code)
                        zip_label = (
                            f"{zip_code} {base_name}"
                            if base_name
                            else (zip_code if zip_code != "Annað" else "Óþekkt")
                        )
                        stats_html += f"<li><strong>{zip_label}:</strong> {zip_avg_m2_formatted} kr.</li>"
            stats_html += "</ul>"

            stats_html += "<h3>Meðalfermetraverð eftir herbergjafjölda:</h3><ul>"
            for bedrooms, avg_price in sorted(avg_price_per_m2.items()):
                avg_price_formatted = f"{avg_price:,}".replace(",", ".")
                stats_html += f"<li><strong>{bedrooms} svefnherbergi:</strong> {avg_price_formatted} kr.</li>"
            stats_html += "</ul></div>"

            html_content = stats_html

            if deal_of_the_day:
                for zip_code in list(properties_by_zip.keys()):
                    if deal_of_the_day in properties_by_zip[zip_code]:
                        properties_by_zip[zip_code].remove(deal_of_the_day)
                        break
                html_content += self.generate_property_html(
                    [deal_of_the_day], "Díll dagsins! 🔥"
                )

            # --- Open Houses Section ---
            open_houses = [
                p
                for p in new_properties
                if p.get("open_house")
                and "fellur niður" not in p.get("open_house").lower()
                and "seld" not in p.get("open_house").lower()
                and "3d = opið hús þegar þér hentar" not in p.get("open_house").lower()
                and "þitt eigið opið hús þegar þér hentar" not in p.get("open_house").lower()
            ]
            if open_houses:
                # We sort them by date if possible, but for now just showing them
                html_content += self.generate_property_html(
                    open_houses, "Næstu opin hús 🏠"
                )

            # --- New Properties Section ---
            if new_since_last_run:
                html_content += self.generate_property_html(
                    new_since_last_run, "Nýjar eignir síðan síðast ✨"
                )

            # --- Property Listings ---
            for zip_code in allowed_zips + ["Annað"]:
                if zip_code in properties_by_zip and properties_by_zip[zip_code]:
                    base_name, dative_name = self._get_location_names(zip_code)
                    title = (
                        f"Fasteignir í {zip_code} {dative_name}"
                        if base_name
                        else (
                            f"Fasteignir í {zip_code}"
                            if zip_code != "Annað"
                            else "Fasteignir (óþekkt póstnúmer)"
                        )
                    )
                    html_content += self.generate_property_html(
                        properties_by_zip[zip_code], title
                    )

            logging.info(
                "Sending email with %d properties to %s",
                len(new_properties),
                self.TO_EMAIL,
            )
            final_html = self.get_email_template(html_content, subject)
            self.send_email_notification(subject, final_html)
        else:
            logging.info(
                "No properties found for user %s. Sending 'no results' email.",
                self.TO_EMAIL,
            )
            subject = "Engar eignir fundust"
            no_results_content = """
                <div style="text-align: center; padding: 40px 20px;">
                    <div style="font-size: 48px; margin-bottom: 20px;">🔍</div>
                    <h2 style="color: #1e293b; margin-bottom: 12px;">Engar eignir fundust</h2>
                    <p style="font-size: 16px; color: #475569; margin-bottom: 24px;">
                        Við leituðum í gegnum allar nýjustu skráningarnar en fundum því miður ekkert sem passaði við þínar kröfur að þessu sinni.
                    </p>
                    <p style="font-size: 14px; color: #64748b; font-style: italic;">
                        Héðan í frá verða öll vettlingatök afnuminn í leit af fasteign fyrir þig!
                    </p>
                </div>
            """
            final_html = self.get_email_template(no_results_content, subject)
            self.send_email_notification(subject, final_html)


def _parse_args():
    parser = argparse.ArgumentParser(description="Scrape real estate listings.")
    parser.add_argument(
        "--user",
        help="Email of the user to run the scraper for.",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run in a loop: each day at 10:00 (default), run for all verified users.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    _configure_logging()
    args = _parse_args()
    if args.schedule:
        run_schedule_loop()
    elif args.user:
        # Fetch specific user from DB
        all_users = get_db_users()
        user_config = next((u for u in all_users if u["user"] == args.user), None)
        if user_config:
            Scraper(user_config).main()
        else:
            logging.error(f"Verified user {args.user} not found in database.")
            raise SystemExit(1)
    else:
        # Default to running once for all users if no args provided?
        # Or just show help. Let's show help.
        print("Usage: scraper.py --schedule OR scraper.py --user EMAIL")
