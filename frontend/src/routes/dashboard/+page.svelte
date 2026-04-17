<script>
    import { onMount } from 'svelte';
    import { getApiUrl } from '$lib/config';
    
    let user = $state(null);
    let minPrice = $state('0');
    let maxPrice = $state('0');
    let minBedrooms = $state(1);
    let maxBedrooms = $state(1);
    let minSize = $state(0);
    let maxSize = $state(1000);
    let minBuildYear = $state(1900);
    let maxBuildYear = $state(2027);
    let scrapeHour = $state(20);
    let emailDays = $state([0, 3]);
    let selectedZipCodes = $state([]);
    let ignoredStreets = $state([]);
    let einbylishus = $state(false);
    let fjolbylishus = $state(false);
    let atvinnuhusnaedi = $state(false);
    let radhus_parhus = $state(false);
    let sumarhus = $state(false);
    let parhus = $state(false);
    let jord_lod = $state(false);
    let haed = $state(false);
    let hesthus = $state(false);
    let oflokkad = $state(false);
    let outdoorFilter = $state('none');
    let want_garage = $state(false);
    let message = $state('');
    let showSuccessModal = $state(false);
    let showEmailSentModal = $state(false);
    let loading = $state(true);
    let showZipDropdown = $state(false);
    let zipDropdownEl = $state(null);
    let pendingStreetName = $state('');
    let selectedPlaceObject = $state(null);

    const googleMapsApiKey = "AIzaSyAAJL11FGR1AImjuxi9kYcxmBTovEZqS7s";

    function setupPlaces(node) {
        let checkGoogle;
        let autocompleteEl;
        
        async function init() {
            const win = /** @type {any} */ (window);
            if (!win.google || !win.google.maps || !win.google.maps.places) {
                return false;
            }

            try {
                node.innerHTML = '';
                
                autocompleteEl = new win.google.maps.places.PlaceAutocompleteElement({
                    componentRestrictions: { country: ['is'] },
                    requestedLanguage: 'is'
                });

                autocompleteEl.id = "street-search";
                autocompleteEl.style.width = "100%";
                autocompleteEl.style.padding = "0.5rem";
                autocompleteEl.style.border = "1px solid #D1D5DB";
                autocompleteEl.style.borderRadius = "0.25rem";
                autocompleteEl.style.outline = "none";
                
                node.appendChild(autocompleteEl);

                autocompleteEl.addEventListener('gmp-placeselect', async (e) => {
                    const place = e.place;
                    if (!place) return;

                    try {
                        // Store the actual place object
                        selectedPlaceObject = place;
                        
                        // Prefetch fields
                        await place.fetchFields({ fields: ['displayName', 'formattedAddress'] });
                        
                        const streetName = place.displayName ? place.displayName.text : place.formattedAddress;
                        if (streetName) {
                            pendingStreetName = streetName.split(',')[0].trim();
                        }
                    } catch (err) {
                        console.error("Error fetching place details:", err);
                    }
                });

                // Also capture manual typing just in case they don't click a suggestion
                autocompleteEl.addEventListener('input', (e) => {
                    // Reset the selected object because they are typing manually now
                    selectedPlaceObject = null;
                    pendingStreetName = e.target?.value || '';
                });

                autocompleteEl.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        // Add a tiny delay to allow placeselect to win if it just happened
                        setTimeout(addPendingStreet, 50);
                    }
                });

                return true;
            } catch (err) {
                console.error("Error initializing PlaceAutocompleteElement:", err);
                return true;
            }
        }

        if (!init()) {
            checkGoogle = setInterval(() => {
                if (init()) clearInterval(checkGoogle);
            }, 100);
        }

        return {
            destroy() {
                if (checkGoogle) clearInterval(checkGoogle);
            }
        };
    }

    async function addPendingStreet() {
        const el = /** @type {any} */ (document.getElementById('street-search'));
        let streetToSave = '';

        if (selectedPlaceObject) {
            // Google Place wins
            try {
                // @ts-ignore
                await selectedPlaceObject.fetchFields({ fields: ['displayName'] });
                // @ts-ignore
                streetToSave = selectedPlaceObject.displayName?.text || selectedPlaceObject.formattedAddress;
            } catch (e) {
                // Fallback
                streetToSave = el?.value || pendingStreetName;
            }
        } else {
            // Manual typing
            streetToSave = el?.value || pendingStreetName;
        }

        if (!streetToSave) return;
        
        // Remove trailing commas if any (e.g. from manual entry)
        const cleanName = streetToSave.split(',')[0].trim();
        
        if (cleanName && !ignoredStreets.includes(cleanName)) {
            ignoredStreets = [...ignoredStreets, cleanName];
            
            // RESET EVERYTHING
            pendingStreetName = '';
            selectedPlaceObject = null;
            
            if (el) {
                el.value = '';
                if (el.inputValue !== undefined) el.inputValue = '';
            }
            
            savePreferences(true);
        }
    }

    function removeStreet(street) {
        ignoredStreets = ignoredStreets.filter(s => s !== street);
        // Auto-save to the database
        savePreferences(true);
    }

    const zipOptionsGrouped = [
        {
            name: "Höfuðborgarsvæðið",
            subgroups: [
                {
                    name: "Reykjavík",
                    options: [
                        { code: "101", name: "Miðbær" }, { code: "102", name: "Vatnsmýri" },
                        { code: "103", name: "Kringlan / Hvassaleiti" }, { code: "104", name: "Vogar" },
                        { code: "105", name: "Austurbær" }, { code: "107", name: "Vesturbær" },
                        { code: "108", name: "Austurbær" }, { code: "109", name: "Seljahverfi" },
                        { code: "110", name: "Árbær" }, { code: "111", name: "Efra Breiðholt" },
                        { code: "112", name: "Grafarvogur" }, { code: "113", name: "Grafarholt" },
                        { code: "116", name: "Kjalarnes" }, { code: "161", name: "Reykjavík" },
                        { code: "162", name: "Kjalarnes" }
                    ]
                },
                {
                    name: "Kópavogur",
                    options: [
                        { code: "200", name: "Kópavogur" }, { code: "201", name: "Kópavogur" },
                        { code: "202", name: "Kópavogur" }, { code: "203", name: "Kópavogur" },
                        { code: "206", name: "Kópavogur" }
                    ]
                },
                {
                    name: "Garðabær",
                    options: [
                        { code: "210", name: "Garðabær" }, { code: "212", name: "Garðabær" },
                        { code: "225", name: "Garðabær" }
                    ]
                },
                {
                    name: "Hafnarfjörður",
                    options: [
                        { code: "220", name: "Hafnarfjörður" }, { code: "221", name: "Hafnarfjörður" },
                        { code: "222", name: "Hafnarfjörður" }
                    ]
                },
                {
                    name: "Mosfellsbær",
                    options: [
                        { code: "270", name: "Mosfellsbær" }, { code: "271", name: "Mosfellsbær" },
                        { code: "276", name: "Mosfellsbær" }
                    ]
                },
                {
                    name: "Seltjarnarnes",
                    options: [
                        { code: "170", name: "Seltjarnarnes" }
                    ]
                }
            ]
        },
        {
            name: "Vesturland",
            options: [
                { code: "300", name: "Akranes" }, { code: "301", name: "Akranes" },
                { code: "310", name: "Borgarnes" }, { code: "311", name: "Borgarnes" },
                { code: "320", name: "Reykholt" }, { code: "340", name: "Stykkishólmur" },
                { code: "345", name: "Flatey" }, { code: "350", name: "Grundarfjörður" },
                { code: "355", name: "Ólafsvík" }, { code: "356", name: "Snæfellsbær" },
                { code: "360", name: "Hellissandur" }, { code: "370", name: "Búðardalur" },
                { code: "371", name: "Búðardalur" }, { code: "380", name: "Reykhólahreppur" }
            ]
        },
        {
            name: "Vestfirðir",
            options: [
                { code: "400", name: "Ísafjörður" }, { code: "401", name: "Ísafjörður" },
                { code: "410", name: "Hnífsdalur" }, { code: "415", name: "Bolungarvík" },
                { code: "416", name: "Bolungarvík" }, { code: "420", name: "Súðavík" },
                { code: "421", name: "Súðavík" }, { code: "425", name: "Flateyri" },
                { code: "426", name: "Flateyri" }, { code: "430", name: "Suðureyri" },
                { code: "431", name: "Suðureyri" }, { code: "450", name: "Patreksfjörður" },
                { code: "451", name: "Patreksfjörður" }, { code: "460", name: "Tálknafjörður" },
                { code: "461", name: "Tálknafjörður" }, { code: "465", name: "Bíldudalur" },
                { code: "466", name: "Bíldudalur" }, { code: "470", name: "Þingeyri" },
                { code: "471", name: "Þingeyri" }
            ]
        },
        {
            name: "Norðurland",
            options: [
                { code: "500", name: "Staður" }, { code: "510", name: "Hólmavík" },
                { code: "511", name: "Hólmavík" }, { code: "512", name: "Hólmavík" },
                { code: "520", name: "Drangsnes" }, { code: "522", name: "Kjörvogur" },
                { code: "523", name: "Bær" }, { code: "524", name: "Norðurfjörður" },
                { code: "530", name: "Hvammstangi" }, { code: "531", name: "Hvammstangi" },
                { code: "540", name: "Blönduós" }, { code: "541", name: "Blönduós" },
                { code: "545", name: "Skagaströnd" }, { code: "546", name: "Skagaströnd" },
                { code: "550", name: "Sauðárkrókur" }, { code: "551", name: "Sauðárkrókur" },
                { code: "560", name: "Varmahlíð" }, { code: "561", name: "Varmahlíð" },
                { code: "565", name: "Hofsós" }, { code: "566", name: "Hofsós" },
                { code: "570", name: "Fljót" }, { code: "580", name: "Siglufjörður" },
                { code: "581", name: "Siglufjörður" }, { code: "600", name: "Akureyri" },
                { code: "601", name: "Akureyri" }, { code: "602", name: "Akureyri" },
                { code: "603", name: "Akureyri" }, { code: "604", name: "Akureyri" },
                { code: "605", name: "Akureyri" }, { code: "606", name: "Akureyri" },
                { code: "607", name: "Akureyri" }, { code: "610", name: "Árskógssandur" },
                { code: "611", name: "Grímsey" }, { code: "616", name: "Grenivík" },
                { code: "620", name: "Dalvík" }, { code: "621", name: "Dalvík" },
                { code: "625", name: "Ólafsfjörður" }, { code: "626", name: "Ólafsfjörður" },
                { code: "630", name: "Hrísey" }, { code: "640", name: "Húsavík" },
                { code: "641", name: "Húsavík" }, { code: "645", name: "Fosshóll" },
                { code: "650", name: "Laugar" }, { code: "660", name: "Mývatn" },
                { code: "670", name: "Kópasker" }, { code: "671", name: "Kópasker" },
                { code: "675", name: "Raufarhöfn" }, { code: "680", name: "Þórshöfn" },
                { code: "681", name: "Þórshöfn" }
            ]
        },
        {
            name: "Austurland",
            options: [
                { code: "700", name: "Egilsstaðir" }, { code: "701", name: "Egilsstaðir" },
                { code: "710", name: "Seyðisfjörður" }, { code: "715", name: "Mjóifjörður" },
                { code: "720", name: "Borgarfjörður eystri" }, { code: "730", name: "Reyðarfjörður" },
                { code: "735", name: "Eskifjörður" }, { code: "740", name: "Neskaupstaður" },
                { code: "750", name: "Fáskrúðsfjörður" }, { code: "755", name: "Stöðvarfjörður" },
                { code: "760", name: "Breiðdalsvík" }, { code: "765", name: "Djúpivogur" },
                { code: "780", name: "Höfn í Hornafirði" }, { code: "781", name: "Höfn í Hornafirði" },
                { code: "785", name: "Öræfi" }
            ]
        },
        {
            name: "Suðurland",
            options: [
                { code: "800", name: "Selfoss" }, { code: "801", name: "Selfoss" },
                { code: "802", name: "Selfoss" }, { code: "803", name: "Selfoss" },
                { code: "804", name: "Selfoss" }, { code: "805", name: "Selfoss" },
                { code: "806", name: "Selfoss" }, { code: "810", name: "Hveragerði" },
                { code: "815", name: "Þorlákshöfn" }, { code: "816", name: "Ölfus" },
                { code: "820", name: "Eyrarbakki" }, { code: "825", name: "Stokkseyri" },
                { code: "840", name: "Laugarvatn" }, { code: "845", name: "Flúðir" },
                { code: "846", name: "Flúðir" }, { code: "850", name: "Hella" },
                { code: "851", name: "Hella" }, { code: "860", name: "Hvolsvöllur" },
                { code: "861", name: "Hvolsvöllur" }, { code: "870", name: "Vík" },
                { code: "871", name: "Vík" }, { code: "880", name: "Kirkjubæjarklaustur" },
                { code: "881", name: "Kirkjubæjarklaustur" }, { code: "900", name: "Vestmannaeyjar" },
                { code: "901", name: "Vestmannaeyjabær" }
            ]
        },
        {
            name: "Suðurnes",
            options: [
                { code: "190", name: "Vogar" }, { code: "191", name: "Vogar" },
                { code: "230", name: "Keflavík" }, { code: "232", name: "Keflavík" },
                { code: "233", name: "Hafnir" }, { code: "240", name: "Grindavík" },
                { code: "241", name: "Grindavík" }, { code: "245", name: "Suðurnesjabær" },
                { code: "246", name: "Suðurnesjabær" }, { code: "250", name: "Suðurnesjabær" },
                { code: "251", name: "Suðurnesjabær" }, { code: "260", name: "Njarðvík" },
                { code: "262", name: "Reykjanesbær" }
            ]
        },
        {
            name: "Útlönd",
            options: [
                { code: "950", name: "Útlönd" }, { code: "951", name: "Útlönd" },
                { code: "952", name: "Útlönd" }, { code: "953", name: "Útlönd" },
                { code: "954", name: "Útlönd" }, { code: "955", name: "Útlönd" },
                { code: "956", name: "Útlönd" }, { code: "970", name: "Útlönd" },
                { code: "971", name: "Útlönd" }, { code: "980", name: "Útlönd" },
                { code: "999", name: "Útlönd" }
            ]
        }
    ];

    let expandedZipGroups = $state({
        "Höfuðborgarsvæðið": false,
        "Reykjavík": false,
        "Kópavogur": false,
        "Garðabær": false,
        "Hafnarfjörður": false,
        "Mosfellsbær": false,
        "Seltjarnarnes": false,
        "Vesturland": false,
        "Vestfirðir": false,
        "Norðurland": false,
        "Austurland": false,
        "Suðurland": false,
        "Suðurnes": false,
        "Útlönd": false,
        "Annað": false
    });

    const zipOptions = zipOptionsGrouped.flatMap(g => g.subgroups ? g.subgroups.flatMap(sg => sg.options) : g.options);

    function toggleZipCode(zipCode) {
        if (selectedZipCodes.includes(zipCode)) {
            selectedZipCodes = selectedZipCodes.filter(z => z !== zipCode);
        } else {
            selectedZipCodes = [...selectedZipCodes, zipCode];
        }
    }

    function toggleZipGroup(groupName) {
        expandedZipGroups[groupName] = !expandedZipGroups[groupName];
    }

    function toggleAllInGroup(options, isChecked) {
        if (isChecked) {
            const codesToAdd = options.map(o => o.code).filter(code => !selectedZipCodes.includes(code));
            selectedZipCodes = [...selectedZipCodes, ...codesToAdd];
        } else {
            const codesToRemove = options.map(o => o.code);
            selectedZipCodes = selectedZipCodes.filter(code => !codesToRemove.includes(code));
        }
    }

    function isGroupFullySelected(options) {
        return options.length > 0 && options.every(o => selectedZipCodes.includes(o.code));
    }

    function toggleEmailDay(day) {
        if (emailDays.includes(day)) {
            emailDays = emailDays.filter(d => d !== day);
        } else {
            emailDays = [...emailDays, day].sort();
        }
    }

    const dayLabels = [
        { id: 0, label: 'Mánudagur', short: 'Mán' },
        { id: 1, label: 'Þriðjudagur', short: 'Þri' },
        { id: 2, label: 'Miðvikudagur', short: 'Mið' },
        { id: 3, label: 'Fimmtudagur', short: 'Fim' },
        { id: 4, label: 'Föstudagur', short: 'Föst' },
        { id: 5, label: 'Laugardagur', short: 'Laug' },
        { id: 6, label: 'Sunnudagur', short: 'Sun' }
    ];

    function getDayLabel(id) {
        return dayLabels.find(d => d.id === id)?.label || '';
    }

    function parseNumber(val) {
        if (!val) return 0;
        return parseInt(String(val).replace(/\./g, ''), 10) || 0;
    }

    function getToken() {
        return document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1];
    }

    async function handleDeleteAccount() {
        if (!confirm('Ertu viss um að þú viljir eyða aðganginum þínum? Þetta er óafturkræft.')) {
            return;
        }

        const token = getToken();
        if (!token) return;

        try {
            const res = await fetch(`${getApiUrl()}/me`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (res.ok) {
                document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                window.location.href = '/home';
            } else {
                message = 'Ekki tókst að eyða aðgangi.';
            }
        } catch (e) {
            message = 'Villa við að tengjast þjóni.';
        }
    }

    async function fetchProfile() {
        const token = getToken();
        if (!token) {
            window.location.href = '/home';
            return;
        }

        try {
            const res = await fetch(`${getApiUrl()}/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (res.ok) {
                user = await res.json();
                if (!user.onboarding_completed) {
                    window.location.href = '/onboarding';
                    return;
                }
                minPrice = formatNumber(user.min_price || 0);
                maxPrice = formatNumber(user.max_price || 0);
                minBedrooms = user.min_bedrooms || 1;
                maxBedrooms = user.max_bedrooms || 1;
                minBuildYear = user.min_build_year || 1900;
                maxBuildYear = user.max_build_year || 2027;
                scrapeHour = user.scrape_hour !== undefined ? user.scrape_hour : 20;
                emailDays = user.email_days || [0, 3];
                selectedZipCodes = (user.zip_codes || []).map(z => {
                    const match = String(z).match(/\d{3}/);
                    return match ? match[0] : null;
                }).filter(z => z !== null);
                ignoredStreets = user.ignored_streets || [];
                einbylishus = user.einbylishus || false;
                fjolbylishus = user.fjolbylishus || false;
                atvinnuhusnaedi = user.atvinnuhusnaedi || false;
                radhus_parhus = user.radhus_parhus || false;
                sumarhus = user.sumarhus || false;
                parhus = user.parhus || false;
                jord_lod = user.jord_lod || false;
                haed = user.haed || false;
                hesthus = user.hesthus || false;
                oflokkad = user.oflokkad || false;
                outdoorFilter = user.outdoor_filter || 'none';
                want_garage = user.want_garage || false;
            } else {
                // Token might be invalid/expired
                document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                window.location.href = '/home';
            }
        } catch (e) {
            message = 'Error connecting to server';
        } finally {
            loading = false;
        }
    }

    async function sendTestEmail() {
        const token = getToken();
        
        try {
            const res = await fetch(`${getApiUrl()}/me/send-test-email`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (res.ok) {
                return true;
            } else {
                const data = await res.json();
                console.error("Failed to send test email:", data.detail);
                return false;
            }
        } catch (e) {
            console.error("Error sending test email:", e);
            return false;
        }
    }

    async function handleSendSettingsEmail() {
        showEmailSentModal = true;
        setTimeout(() => { showEmailSentModal = false; }, 5000);
        
        // Perform saving and sending in the background without blocking the UI
        savePreferences(true).then(saveOk => {
            if (saveOk) {
                sendTestEmail();
            }
        });
    }


    let isSaving = $state(false);

    async function savePreferences(silent = false) {
        if (!silent) {
            // Basic range validation
            if (minBedrooms > maxBedrooms) {
                message = 'Lágmarksfjöldi svefnherbergja getur ekki verið meiri en hámarksfjöldi.';
                return false;
            }
            if (parseNumber(minPrice) > parseNumber(maxPrice)) {
                message = 'Lágmarksverð getur ekki verið hærra en hámarksverð.';
                return false;
            }
            if (minSize > maxSize) {
                message = 'Lágmarksstærð getur ekki verið meiri en hámarksstærð.';
                return false;
            }
            if (minBuildYear > maxBuildYear) {
                message = 'Elsta byggingarár getur ekki verið hærra en nýjasta byggingarár.';
                return false;
            }
        }

        const token = getToken();
        if (!silent) {
            isSaving = true;
            message = 'Vistar...';
        }
        
        try {
            const res = await fetch(`${getApiUrl()}/me/preferences`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    min_price: parseNumber(minPrice),
                    max_price: parseNumber(maxPrice),
                    min_bedrooms: minBedrooms,
                    max_bedrooms: maxBedrooms,
                    min_size: minSize,
                    max_size: maxSize,
                    min_build_year: minBuildYear,
                    max_build_year: maxBuildYear,
                    scrape_hour: scrapeHour,
                    email_days: emailDays,
                    zip_codes: selectedZipCodes,
                    ignored_streets: ignoredStreets,
                    einbylishus: einbylishus,
                    fjolbylishus: fjolbylishus,
                    atvinnuhusnaedi: atvinnuhusnaedi,
                    radhus_parhus: radhus_parhus,
                    sumarhus: sumarhus,
                    parhus: parhus,
                    jord_lod: jord_lod,
                    haed: haed,
                    hesthus: hesthus,
                    oflokkad: oflokkad,
                    outdoor_filter: outdoorFilter,
                    want_garage: want_garage,
                    onboarding_completed: true
                })
            });

            if (res.ok) {
                if (!silent) {
                    message = 'Vistað!';
                    showSuccessModal = true;
                    setTimeout(() => {
                        if (message === 'Vistað!') message = '';
                    }, 3000);
                }
                return true;
            } else {
                if (!silent) message = 'Ekki tókst að vista stillingar.';
                return false;
            }
        } catch (e) {
            if (!silent) message = 'Villa við að vista stillingar.';
            return false;
        } finally {
            if (!silent) isSaving = false;
        }
    }

    onMount(() => {
        fetchProfile();

        const handleClickOutside = (event) => {
            if (showZipDropdown && zipDropdownEl && !zipDropdownEl.contains(event.target)) {
                showZipDropdown = false;
            }
        };

        window.addEventListener('click', handleClickOutside);

        if (!window.google) {
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places&loading=async`;
            script.async = true;
            script.defer = true;
            document.head.appendChild(script);
        }

        return () => {
            window.removeEventListener('click', handleClickOutside);
        };
    });
</script>

<div class="p-8 max-w-2xl mx-auto">
    <div class="fixed top-0 left-0 p-4 z-50">
        <a href="/home" class="flex items-center hover:opacity-90 transition-opacity">
            <span class="font-bold text-4xl md:text-5xl tracking-tight text-blue-500 mt-2 ml-1" style="letter-spacing: -0.02em;">Fundvís</span>
        </a>
    </div>

    <div class="fixed top-0 right-0 pt-10 pr-6 md:pr-10 lg:pt-12 flex gap-2 z-50">
        <button
            onclick={() => { document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"; window.location.href = '/home'; }}
            class="bg-gray-100 text-gray-700 px-4 py-2 rounded-full border border-gray-300 hover:bg-gray-200 transition-colors font-semibold text-sm shadow-sm"
        >
            Útskráning
        </button>
    </div>
    
    {#if user}
        {#if !user.is_pro}
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8 mt-12 rounded-md shadow-sm">
                <div class="flex items-center justify-between w-full">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-yellow-700 font-medium">
                                Þú ert á prufureikning, til þess að hafa fullt aðgengi að öllum eiginleikum síðunnar verður þú að kaupa áskrift.
                            </p>
                        </div>
                    </div>
                    <div class="ml-4">
                        <a href="/upgrade" class="inline-block bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded shadow transition-colors">
                            Kaupa áskrift
                        </a>
                    </div>
                </div>
            </div>
        {:else}
            <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-8 mt-12 rounded-md shadow-sm">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-green-700 font-medium">
                            Þú ert með virka áskrift og hefur aðgengi að öllum eiginleikum síðunnar.
                        </p>
                    </div>
                </div>
            </div>
        {/if}
    {/if}

    <div class="flex justify-center items-center mb-8 text-center mt-6">
        <h1 class="text-3xl font-bold">Finndu fasteign sem segir já!</h1>
    </div>

    {#if loading}
        <p>Loading your profile...</p>
    {:else if user}
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <!-- Verð og stærð Section -->
            <div class="mb-10">
                
                <div class="mb-8 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Verð</span>
                    <div class="grid grid-cols-2 gap-4 w-full">
                        <div class="flex flex-col items-center">
                            <label for="minPrice" class="block text-sm font-bold text-gray-700 mb-2">Lágmarksverð</label>
                            <div class="relative w-full">
                                <input 
                                    type="text" 
                                    inputmode="numeric"
                                    id="minPrice" 
                                    value={minPrice}
                                    oninput={(e) => minPrice = formatNumber(e.target.value)}
                                    class="w-full p-3 pr-12 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-center text-lg font-semibold"
                                />
                                <span class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold text-lg">kr.</span>
                            </div>
                        </div>
                        <div class="flex flex-col items-center">
                            <label for="maxPrice" class="block text-sm font-bold text-gray-700 mb-2">Hámarksverð</label>
                            <div class="relative w-full">
                                <input 
                                    type="text" 
                                    inputmode="numeric"
                                    id="maxPrice" 
                                    value={maxPrice}
                                    oninput={(e) => maxPrice = formatNumber(e.target.value)}
                                    class="w-full p-3 pr-12 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-center text-lg font-semibold"
                                />
                                <span class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold text-lg">kr.</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mb-8 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Fjöldi svefnherbergja</span>
                    <div class="grid grid-cols-2 gap-4 w-full">
                        <div class="flex flex-col items-center">
                            <span class="block text-sm font-bold text-gray-700 mb-2 text-center">Lágmarksfjöldi</span>
                            <div class="flex items-center gap-4">
                                <button 
                                    type="button" 
                                    onclick={() => minBedrooms = Math.max(0, minBedrooms - 1)}
                                    class="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold transition-colors"
                                >−</button>
                                <div class="w-12 h-12 rounded-full border-2 border-blue-500 flex items-center justify-center text-xl font-bold text-blue-700">
                                    {minBedrooms}
                                </div>
                                <button 
                                    type="button" 
                                    onclick={() => {
                                        minBedrooms++;
                                        if (minBedrooms > maxBedrooms) maxBedrooms = minBedrooms;
                                    }}
                                    class="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold transition-colors"
                                >+</button>
                            </div>
                        </div>
                        <div class="flex flex-col items-center">
                            <span class="block text-sm font-bold text-gray-700 mb-2 text-center">Hámarksfjöldi</span>
                            <div class="flex items-center gap-4">
                                <button 
                                    type="button" 
                                    onclick={() => {
                                        maxBedrooms = Math.max(0, maxBedrooms - 1);
                                        if (maxBedrooms < minBedrooms) minBedrooms = maxBedrooms;
                                    }}
                                    class="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold transition-colors"
                                >−</button>
                                <div class="w-12 h-12 rounded-full border-2 border-blue-500 flex items-center justify-center text-xl font-bold text-blue-700">
                                    {maxBedrooms}
                                </div>
                                <button 
                                    type="button" 
                                    onclick={() => maxBedrooms++}
                                    class="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold transition-colors"
                                >+</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mb-8 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Stærð (m²)</span>
                    <div class="grid grid-cols-2 gap-8 w-full max-w-sm">
                        <div class="flex flex-col items-center">
                            <label for="minSize" class="block text-sm font-bold text-gray-700 mb-2">Lágmarksstærð</label>
                            <div class="relative w-full">
                                <input
                                    type="number"
                                    id="minSize"
                                    bind:value={minSize}
                                    class="w-full p-3 pr-10 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-center text-lg font-semibold"
                                />
                                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">m²</span>
                            </div>
                        </div>
                        <div class="flex flex-col items-center">
                            <label for="maxSize" class="block text-sm font-bold text-gray-700 mb-2">Hámarksstærð</label>
                            <div class="relative w-full">
                                <input
                                    type="number"
                                    id="maxSize"
                                    bind:value={maxSize}
                                    class="w-full p-3 pr-10 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-center text-lg font-semibold"
                                />
                                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">m²</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mb-4 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Byggingarár</span>
                    <div class="grid grid-cols-2 gap-4 w-full">
                        <div class="flex flex-col items-center">
                            <span class="block text-sm font-bold text-gray-700 mb-2 text-center">Elsta ár</span>
                            <select 
                                bind:value={minBuildYear}
                                class="w-full max-w-[200px] p-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none bg-white text-center font-semibold text-lg"
                            >
                                {#each Array.from({ length: 2027 - 1800 + 1 }, (_, i) => 1800 + i) as year}
                                    <option value={year}>{year}</option>
                                {/each}
                            </select>
                        </div>
                        <div class="flex flex-col items-center">
                            <span class="block text-sm font-bold text-gray-700 mb-2 text-center">Nýjasta ár</span>
                            <select 
                                bind:value={maxBuildYear}
                                class="w-full max-w-[200px] p-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none bg-white text-center font-semibold text-lg"
                            >
                                {#each Array.from({ length: 2027 - 1800 + 1 }, (_, i) => 1800 + i) as year}
                                    <option value={year}>{year}</option>
                                {/each}
                            </select>
                        </div>
                    </div>
                </div>
            </div>

        <!-- Staðsetning Section -->
        <div class="mb-10">
            <div class="mb-8 relative flex flex-col items-center w-full" bind:this={zipDropdownEl}>
                <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Póstnúmer</span>
                <div class="relative w-full max-w-sm">
                    <button 
                        type="button"
                        onclick={(e) => { e.stopPropagation(); showZipDropdown = !showZipDropdown; }}
                        class="w-full text-left p-4 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none bg-white flex justify-between items-center text-center font-semibold"
                    >
                        <span class="w-full text-center truncate">
                            Veldu póstnúmer
                        </span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 shrink-0" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                    
                    {#if showZipDropdown}
                        <div class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded shadow-lg">
                            <ul class="max-h-[700px] overflow-auto py-1">
                                {#each zipOptionsGrouped as group}
                                    <li>
                                        <button 
                                            type="button" 
                                            onclick={() => toggleZipGroup(group.name)}
                                            class="flex justify-between items-center w-full px-4 py-2 bg-gray-50 hover:bg-gray-100 font-semibold text-gray-700 text-left cursor-pointer border-b border-gray-200"
                                        >
                                            <span>{group.name}</span>
                                            <svg 
                                                xmlns="http://www.w3.org/2000/svg" 
                                                class="h-4 w-4 transform transition-transform {expandedZipGroups[group.name] ? 'rotate-180' : ''}" 
                                                viewBox="0 0 20 20" 
                                                fill="currentColor"
                                            >
                                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                            </svg>
                                        </button>
                                        {#if expandedZipGroups[group.name]}
                                            <ul class="border-b border-gray-100 pb-1">
                                                {#if group.subgroups}
                                                    <li>
                                                        <label class="flex items-center px-4 py-1.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100">
                                                            <input 
                                                                type="checkbox" 
                                                                class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                                checked={isGroupFullySelected(group.subgroups.flatMap(sg => sg.options))}
                                                                onchange={(e) => toggleAllInGroup(group.subgroups.flatMap(sg => sg.options), e.target.checked)}
                                                            />
                                                            <span class="ml-3 text-sm font-bold text-gray-700">Velja allt í {group.name}</span>
                                                        </label>
                                                    </li>
                                                    {#each group.subgroups as subgroup}
                                                        <li>
                                                            <button 
                                                                type="button" 
                                                                onclick={() => toggleZipGroup(subgroup.name)}
                                                                class="flex justify-between items-center w-full px-6 py-2 bg-white hover:bg-gray-50 font-medium text-gray-600 text-left cursor-pointer border-t border-gray-100"
                                                            >
                                                                <span>{subgroup.name}</span>
                                                                <svg 
                                                                    xmlns="http://www.w3.org/2000/svg" 
                                                                    class="h-3 w-3 transform transition-transform {expandedZipGroups[subgroup.name] ? 'rotate-180' : ''}" 
                                                                    viewBox="0 0 20 20" 
                                                                    fill="currentColor"
                                                                >
                                                                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                                                </svg>
                                                            </button>
                                                            {#if expandedZipGroups[subgroup.name]}
                                                                <ul class="pl-6 border-t border-gray-100 py-1 bg-gray-50 bg-opacity-50">
                                                                    <li>
                                                                        <label class="flex items-center px-4 py-1.5 hover:bg-gray-100 cursor-pointer border-b border-gray-200">
                                                                            <input 
                                                                                type="checkbox" 
                                                                                class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                                                checked={isGroupFullySelected(subgroup.options)}
                                                                                onchange={(e) => toggleAllInGroup(subgroup.options, e.target.checked)}
                                                                            />
                                                                            <span class="ml-3 text-sm font-bold text-gray-700">Velja allt</span>
                                                                        </label>
                                                                    </li>
                                                                    {#each subgroup.options as option}
                                                                        <li>
                                                                            <label class="flex items-center px-4 py-1.5 hover:bg-gray-100 cursor-pointer">
                                                                                <input 
                                                                                    type="checkbox" 
                                                                                    class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                                                    checked={selectedZipCodes.includes(option.code)}
                                                                                    onchange={() => toggleZipCode(option.code)}
                                                                                />
                                                                                <span class="ml-3 text-sm text-gray-700">{option.code} {option.name}</span>
                                                                            </label>
                                                                        </li>
                                                                    {/each}
                                                                </ul>
                                                            {/if}
                                                        </li>
                                                    {/each}
                                                {:else}
                                                    <ul class="pl-4 py-1">
                                                        <li>
                                                            <label class="flex items-center px-4 py-1.5 hover:bg-gray-100 cursor-pointer border-b border-gray-100">
                                                                <input 
                                                                    type="checkbox" 
                                                                    class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                                    checked={isGroupFullySelected(group.options)}
                                                                    onchange={(e) => toggleAllInGroup(group.options, e.target.checked)}
                                                                />
                                                                <span class="ml-3 text-sm font-bold text-gray-700">Velja allt</span>
                                                            </label>
                                                        </li>
                                                        {#each group.options as option}
                                                            <li>
                                                                <label class="flex items-center px-4 py-1.5 hover:bg-gray-100 cursor-pointer">
                                                                    <input 
                                                                        type="checkbox" 
                                                                        class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                                        checked={selectedZipCodes.includes(option.code)}
                                                                        onchange={() => toggleZipCode(option.code)}
                                                                    />
                                                                    <span class="ml-3 text-sm text-gray-700">{option.code} {option.name}</span>
                                                                </label>
                                                            </li>
                                                        {/each}
                                                    </ul>
                                                {/if}
                                            </ul>
                                        {/if}
                                    </li>
                                {/each}
                            </ul>
                        </div>
                    {/if}
                </div>

                {#if selectedZipCodes.length > 0}
                    <div class="mt-4 flex flex-wrap gap-2 w-full max-w-lg">
                        {#each selectedZipCodes as code}
                            <span class="inline-flex items-center bg-blue-50 text-blue-700 text-sm font-bold px-3 py-1.5 rounded-full border border-blue-200 shadow-sm transition-all hover:shadow hover:bg-blue-100">
                                {zipOptions.find(o => o.code === String(code))?.code || code}
                                <button 
                                    type="button" 
                                    aria-label="Remove {code}"
                                    onclick={(e) => { e.stopPropagation(); toggleZipCode(code); }}
                                    class="ml-2 text-blue-400 hover:text-blue-600 focus:outline-none transition-colors"
                                >
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                                </button>
                            </span>
                        {/each}
                    </div>
                {/if}
            </div>

            <div class="mb-8 flex flex-col items-center w-full">
                <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Götur sem á að hunsa</span>
                <div class="mb-3 flex items-center gap-2 w-full max-w-lg">
                    <div class="w-full flex-grow" use:setupPlaces>
                        <!-- Google Maps PlaceAutocompleteElement will inject here -->
                    </div>
                    <button 
                        type="button"
                        onclick={addPendingStreet}
                        disabled={!pendingStreetName}
                        class="border-2 border-blue-600 text-blue-600 px-6 py-2 h-[42px] rounded-xl font-bold hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap bg-white"
                    >
                        Bæta við
                    </button>
                </div>
                
                {#if ignoredStreets.length > 0}
                    <div class="flex flex-wrap gap-2">
                        {#each ignoredStreets as street}
                            <span class="inline-flex items-center bg-gray-100 text-gray-800 text-sm font-medium px-3 py-1 rounded-full border border-gray-300">
                                {street}
                                <button 
                                    type="button"
                                    onclick={() => removeStreet(street)}
                                    class="ml-2 text-gray-500 hover:text-red-500 focus:outline-none"
                                    title="Fjarlægja götu"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </span>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>

        <!-- Eiginleikar Section -->
            <div class="mb-10">
                <div class="mb-8 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Tegundir eigna</span>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 w-full">
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {einbylishus ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={einbylishus} class="hidden" />
                            <span class="text-sm font-bold text-center">Einbýlishús</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {parhus ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={parhus} class="hidden" />
                            <span class="text-sm font-bold text-center">Parhús</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {radhus_parhus ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={radhus_parhus} class="hidden" />
                            <span class="text-sm font-bold text-center">Raðhús</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {fjolbylishus ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={fjolbylishus} class="hidden" />
                            <span class="text-sm font-bold text-center">Fjölbýlishús</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {haed ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={haed} class="hidden" />
                            <span class="text-sm font-bold text-center">Hæð</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {atvinnuhusnaedi ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={atvinnuhusnaedi} class="hidden" />
                            <span class="text-sm font-bold text-center">Atvinnuhúsnæði</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {sumarhus ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={sumarhus} class="hidden" />
                            <span class="text-sm font-bold text-center">Sumarhús</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {jord_lod ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={jord_lod} class="hidden" />
                            <span class="text-sm font-bold text-center">Jörð/Lóð</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {hesthus ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={hesthus} class="hidden" />
                            <span class="text-sm font-bold text-center">Hesthús</span>
                        </label>
                        <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {oflokkad ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                            <input type="checkbox" bind:checked={oflokkad} class="hidden" />
                            <span class="text-sm font-bold text-center">Óflokkað</span>
                        </label>
                    </div>
                </div>

                <div class="mb-8 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Svalir og garður</span>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 w-full">
                        {#each [
                            { val: 'balcony', label: 'Bara svalir' },
                            { val: 'garden', label: 'Bara garður' },
                            { val: 'either', label: 'Annað hvort' },
                            { val: 'both', label: 'Bæði' },
                            { val: 'none', label: 'Skiptir ekki máli' }
                        ] as opt}
                            <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {outdoorFilter === opt.val ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'}">
                                <input type="radio" name="outdoorFilter" value={opt.val} bind:group={outdoorFilter} class="hidden" />
                                <span class="text-sm font-bold text-center">{opt.label}</span>
                            </label>
                        {/each}
                    </div>
                </div>

                <div class="mb-4 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Bílskúr</span>
                    <label class="flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer transition-all {want_garage ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600'} w-full max-w-[200px]">
                        <input type="checkbox" bind:checked={want_garage} class="hidden" />
                        <span class="text-sm font-bold text-center">Bílskúr nauðsynlegur</span>
                    </label>
                </div>
            </div>

        <hr class="border-gray-100 my-10 w-full" />

        <!-- Stillingar tölvupósts Section -->
            <div class="mb-6">
                
                <div class="mb-8 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Dagar sem þú færð tölvupóst</span>
                    <div class="flex flex-wrap justify-center gap-2 w-full">
                        {#each dayLabels as day}
                            <button
                                type="button"
                                onclick={() => toggleEmailDay(day.id)}
                                class="px-3 py-2 rounded-xl border-2 font-bold transition-all text-sm {emailDays.includes(day.id) ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-100 text-gray-600 hover:border-gray-200'}"
                            >
                                {day.label}
                            </button>
                        {/each}
                    </div>
                </div>

                <div class="mb-8 flex flex-col items-center w-full">
                    <span class="block text-sm uppercase tracking-wider font-bold text-gray-500 mb-3 text-center">Klukkan hvað færðu tölvupóstinn?</span>
                    <select 
                        bind:value={scrapeHour}
                        class="w-full max-w-[200px] p-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none bg-white text-center font-semibold text-lg"
                    >
                        {#each Array(24) as _, i}
                            <option value={i}>{i}:00</option>
                        {/each}
                    </select>
                </div>
            </div>

            <div class="flex flex-col items-center gap-8 py-8">
                <div class="flex flex-col items-center gap-4">
                    <button 
                        onclick={() => savePreferences(false)}
                        disabled={isSaving}
                        class="px-12 py-6 rounded-full bg-blue-600 text-white font-bold text-xl hover:bg-blue-700 transition-all shadow-lg hover:scale-105 active:scale-95 flex items-center justify-center text-center disabled:opacity-50 disabled:cursor-not-allowed min-w-[240px]"
                    >
                        {isSaving ? 'Vistar...' : 'Vista stillingar'}
                    </button>
                    
                    <button 
                        onclick={handleSendSettingsEmail}
                        class="px-8 py-4 rounded-full border-2 border-green-600 text-green-600 bg-white font-bold text-lg hover:bg-green-50 transition-all hover:scale-105 active:scale-95 flex items-center justify-center text-center"
                    >
                        Senda tölvupóst með þessum stillingum
                    </button>
                </div>
                
                {#if message}
                    <span class="text-sm font-medium {message.includes('Error') || message.includes('Failed') || message.includes('Villa') || message.includes('Ekki') ? 'text-red-500' : 'text-green-600'}">
                        {message}
                    </span>
                {/if}
            </div>
        </div>

        <div class="mt-8 text-center flex flex-col items-center gap-4">
            <p class="text-gray-500 italic text-sm">Signed in as: {user.email}</p>
            <button 
                onclick={handleDeleteAccount}
                class="text-gray-400 hover:text-gray-600 text-sm underline transition-colors"
            >
                Eyða aðgangi
            </button>
        </div>
    {/if}

    {#if showSuccessModal}
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-white/40 backdrop-blur-sm">
            <div class="bg-white rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl border border-gray-200 transform transition-all">
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                </div>
                <h3 class="text-2xl font-bold text-gray-900 mb-2">Frábært!</h3>
                <p class="text-gray-600 mb-8">
                    Þú hefur vistað stillingar. Þú munt fá tölvupóst kl. {scrapeHour}:00 á 
                    {#if emailDays.length === 7}
                        hverjum degi
                    {:else if emailDays.length === 0}
                        engum degi (vaktin er óvirk)
                    {:else}
                        {emailDays.map(d => getDayLabel(d).toLowerCase()).join(', ')}
                    {/if}
                    með eignum sem passa við þínar kröfur.
                </p>
                <div class="flex flex-col gap-3">
                    <button
                        onclick={() => showSuccessModal = false}
                        class="w-full bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 transition-colors"
                    >
                        Loka
                    </button>
                    <button
                        onclick={() => { showSuccessModal = false; showEmailSentModal = true; sendTestEmail(); }}
                        class="w-full bg-green-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-green-700 transition-colors shadow-md"
                    >
                        Fá prufutölvupóst núna
                    </button>
                </div>
            </div>
        </div>
    {/if}

    {#if showEmailSentModal}
        <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-white/40 backdrop-blur-sm">
            <div class="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl transition-all border border-gray-100 flex flex-col items-center text-center gap-6">
                <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
                    <svg class="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </div>
                <div class="flex-grow">
                    <p class="text-gray-800 text-2xl font-bold mb-2">Póstur í vinnslu!</p>
                    <p class="text-gray-600 text-lg mb-6">Tölvupóstur er í vinnslu, fylgstu vel með!</p>
                    <button
                        onclick={() => showEmailSentModal = false}
                        class="w-full bg-blue-600 text-white font-bold text-lg px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors shadow-md"
                    >
                        Loka
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>
