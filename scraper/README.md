# Property scraper

Scrapes [Fasteignir.is](https://fasteignir.visir.is) listings for verified users in the database and sends email summaries via Brevo.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables (`.env`)

The scraper requires a `.env` file in the `scraper/` directory with the following variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | SQLAlchemy-compatible database URL (e.g., `postgresql://user:pass@localhost/dbname`) |
| `BREVO_API_KEY` | Yes | API key for sending emails via Brevo |
| `FROM_EMAIL` | Yes | The email address shown as the sender |
| `SCRAPER_HOUR` | No | Hour (0–23) to run daily in `--schedule` mode (Default: 10) |
| `SCRAPER_MINUTE` | No | Minute (0–59) to run daily in `--schedule` mode (Default: 0) |

## Usage

The scraper now fetches user preferences directly from the `users` table in the database. Only **verified** users (`is_verified = True`) are processed.

### One-off run (single user)

Runs the scrape, filters, and emails once for the given user's email:

```bash
python scraper.py --user test@example.com
```

### Scheduled runs (daemon)

Runs indefinitely, executing once per calendar day at the specified time (defaulting to 10:00 AM). It processes all verified users in parallel.

```bash
python scraper.py --schedule
```

**Do not** pass `--user` together with `--schedule`.

### systemd (Raspberry Pi / server)

A systemd service file is provided in `services/scraper.service`. It is configured to run in `--schedule` mode.

To install:
1. Ensure `DATABASE_URL`, `BREVO_API_KEY`, and `FROM_EMAIL` are in `/opt/properties-by-magni/scraper/.env`.
2. Copy the service file: `sudo cp services/scraper.service /etc/systemd/system/`
3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scraper.service
```

---

## Technical Details

- **Database**: Uses SQLAlchemy to connect to the shared application database.
- **Concurrency**: Uses `ThreadPoolExecutor` to fetch property details and process multiple users in parallel.
- **Filters**: Supports filtering by price, bedrooms, zip codes, property types (house, apartment, etc.), outdoor space (balcony/garden), and garage.
- **Emails**: Sends rich HTML emails with property images (embedded as data URIs) and price statistics.
