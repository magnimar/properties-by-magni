<script>
    import { onMount } from 'svelte';
    import { getApiUrl } from '$lib/config';
    
    let user = $state(null);
    let step = $state(0); // 0: Intro, 1: Min Price, 2: Max Price, 3: Bedrooms, 4: Build Year, 5: Zip Codes, 6: Property Types, 7: Outdoor, 8: Garage, 9: Review
    
    let minPrice = $state('0');
    let maxPrice = $state('0');
    let minBedrooms = $state(1);
    let maxBedrooms = $state(1);
    let minBuildYear = $state(1900);
    let maxBuildYear = $state(2027);
    let selectedZipCodes = $state([]);
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
    let loading = $state(true);
    let showZipDropdown = $state(false);
    let showSuccessModal = $state(false);
    let showEmailSentModal = $state(false);

    function formatNumber(val) {
        if (!val && val !== 0) return '';
        let num = String(val).replace(/\./g, '').replace(/\D/g, '');
        return num ? parseInt(num, 10).toLocaleString('de-DE') : '';
    }

    function parseNumber(val) {
        if (!val) return 0;
        return parseInt(String(val).replace(/\./g, ''), 10) || 0;
    }

    function getToken() {
        return document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1];
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
                if (user.onboarding_completed) {
                    window.location.href = '/dashboard';
                    return;
                }
                // Initialize with existing data if any
                minPrice = formatNumber(user.min_price || 0);
                maxPrice = formatNumber(user.max_price || 0);
                minBedrooms = user.min_bedrooms || 1;
                maxBedrooms = user.max_bedrooms || 1;
                minBuildYear = user.min_build_year || 1900;
                maxBuildYear = user.max_build_year || 2027;
                selectedZipCodes = user.zip_codes || [];
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
                window.location.href = '/home';
            }
        } catch (e) {
            message = 'Error connecting to server';
        } finally {
            loading = false;
        }
    }

    async function saveOnboarding(isFinal = false) {
        const token = getToken();
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
                    min_build_year: minBuildYear,
                    max_build_year: maxBuildYear,
                    zip_codes: selectedZipCodes,
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
                    onboarding_completed: isFinal
                })
            });

            if (res.ok) {
                if (isFinal) {
                    showSuccessModal = true;
                }
            } else {
                message = 'Failed to save progress.';
            }
        } catch (e) {
            message = 'Error saving preferences.';
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

            if (!res.ok) {
                const data = await res.json();
                console.error("Failed to send test email:", data.detail);
            }
        } catch (e) {
            console.error("Error sending test email:", e);
        }
    }

    function nextStep() {
        if (step === 2) {
            const price = parseNumber(maxPrice);
            if (price < 40000000) {
                message = 'Vinsamlegast sláðu inn hámarksverð sem er að minnsta kosti 40.000.000 ISK.';
                return;
            }
        }
        
        if (step === 4 && selectedZipCodes.length === 0) {
            message = 'Vinsamlegast veldu að minnsta kosti eitt póstnúmer til að halda áfram.';
            return;
        }

        if (step === 5) {
            if (!(einbylishus || fjolbylishus || radhus_parhus || parhus || haed || sumarhus || jord_lod || atvinnuhusnaedi || hesthus || oflokkad)) {
                message = 'Vinsamlegast veldu að minnsta kosti eina tegund eignar.';
                return;
            }
        }

        message = ''; // Clear message if validation passes

        if (step < 9) {
            step++;
            // Optional: Auto-save at each step
            saveOnboarding(false);
        } else {
            saveOnboarding(true);
        }
    }

    function prevStep() {
        if (step > 0) {
            step--;
        }
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

    let expandedZipGroups = $state({});

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

    function getSelectedPropertyTypes() {
        const types = [];
        if (einbylishus) types.push('Einbýlishús');
        if (fjolbylishus) types.push('Fjölbýlishús');
        if (radhus_parhus) types.push('Raðhús / Parhús');
        if (haed) types.push('Hæð');
        if (sumarhus) types.push('Sumarhús');
        if (jord_lod) types.push('Jörð / Lóð');
        if (atvinnuhusnaedi) types.push('Atvinnuhúsnæði');
        return types.length > 0 ? types.join(', ') : 'Allar tegundir';
    }

    onMount(() => {
        fetchProfile();
    });
</script>

<div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div class="max-w-xl w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        {#if loading}
            <div class="p-12 text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p class="mt-4 text-gray-600">Sæki upplýsingar...</p>
            </div>
        {:else if user}
            <!-- Progress Bar -->
            <div class="h-2 bg-gray-100">
                <div 
                    class="h-full bg-blue-600 transition-all duration-500 ease-out" 
                    style="width: {(step / 9) * 100}%"
                ></div>
            </div>

            <div class="p-8 md:p-12">
                {#if step === 0}
                    <div class="text-center">
                        <h1 class="text-3xl font-bold text-gray-900 mb-8">Velkomin/n í Properties by Magni!</h1>
                        <button 
                            onclick={nextStep}
                            class="w-full bg-blue-600 text-white py-4 rounded-xl font-bold text-lg hover:bg-blue-700 transition-colors shadow-lg"
                        >
                            Hefja uppsetningu
                        </button>
                    </div>

                {:else if step === 1}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Hvert er lágmarksverðið?</h2>
                        <p class="text-gray-600 mb-8">Sláðu inn lægsta verðið sem þú ert að skoða.</p>
                        <div class="relative">
                            <input 
                                type="text" 
                                inputmode="numeric"
                                bind:value={minPrice}
                                oninput={(e) => minPrice = formatNumber(e.target.value)}
                                class="w-full p-4 text-2xl border-2 border-gray-200 rounded-xl focus:border-blue-500 outline-none transition-colors"
                                placeholder="0"
                            />
                            <span class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold">ISK</span>
                        </div>
                    </div>

                {:else if step === 2}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Hvert er hámarksverðið?</h2>
                        <p class="text-gray-600 mb-8">Hvað er mesta sem þú vilt borga?</p>
                        <div class="relative">
                            <input 
                                type="text" 
                                inputmode="numeric"
                                bind:value={maxPrice}
                                oninput={(e) => maxPrice = formatNumber(e.target.value)}
                                class="w-full p-4 text-2xl border-2 border-gray-200 rounded-xl focus:border-blue-500 outline-none transition-colors"
                                placeholder="0"
                            />
                            <span class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold">ISK</span>
                        </div>
                    </div>

                {:else if step === 3}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-8">Svefnherbergi</h2>
                        <div class="grid grid-cols-2 gap-8">
                            <div class="flex flex-col items-center">
                                <label class="block text-xl font-bold text-gray-700 mb-4">Lágmarksfjöldi</label>
                                <div class="flex items-center gap-4">
                                    <div class="w-16 h-16 rounded-full border-4 border-blue-500 flex items-center justify-center text-2xl font-bold text-blue-700">
                                        {minBedrooms}
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <button 
                                            type="button" 
                                            onclick={() => minBedrooms++}
                                            class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold text-xl transition-colors"
                                        >+</button>
                                        <button 
                                            type="button" 
                                            onclick={() => minBedrooms = Math.max(0, minBedrooms - 1)}
                                            class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold text-xl transition-colors"
                                        >−</button>
                                    </div>
                                </div>
                            </div>
                            <div class="flex flex-col items-center">
                                <label class="block text-xl font-bold text-gray-700 mb-4">Hámarksfjöldi</label>
                                <div class="flex items-center gap-4">
                                    <div class="w-16 h-16 rounded-full border-4 border-blue-500 flex items-center justify-center text-2xl font-bold text-blue-700">
                                        {maxBedrooms}
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <button 
                                            type="button" 
                                            onclick={() => maxBedrooms++}
                                            class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold text-xl transition-colors"
                                        >+</button>
                                        <button 
                                            type="button" 
                                            onclick={() => maxBedrooms = Math.max(0, maxBedrooms - 1)}
                                            class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold text-xl transition-colors"
                                        >−</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                {:else if step === 4}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-8">Byggingarár</h2>
                        <div class="grid grid-cols-2 gap-8">
                            <div class="flex flex-col items-center">
                                <label class="block text-xl font-bold text-gray-700 mb-4">Elsta ár</label>
                                <div class="flex items-center gap-4">
                                    <div class="px-4 h-16 rounded-full border-4 border-blue-500 flex items-center justify-center text-2xl font-bold text-blue-700">
                                        {minBuildYear}
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <button 
                                            type="button" 
                                            onclick={() => minBuildYear++}
                                            class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold text-xl transition-colors"
                                        >+</button>
                                        <button 
                                            type="button" 
                                            onclick={() => minBuildYear = Math.max(1800, minBuildYear - 1)}
                                            class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold text-xl transition-colors"
                                        >−</button>
                                    </div>
                                </div>
                            </div>
                            <div class="flex flex-col items-center">
                                <label class="block text-xl font-bold text-gray-700 mb-4">Nýjasta ár</label>
                                <div class="flex items-center gap-4">
                                    <div class="px-4 h-16 rounded-full border-4 border-blue-500 flex items-center justify-center text-2xl font-bold text-blue-700">
                                        {maxBuildYear}
                                    </div>
                                    <div class="flex flex-col gap-2">
                                        <button 
                                            type="button" 
                                            onclick={() => maxBuildYear++}
                                            class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold text-xl transition-colors"
                                        >+</button>
                                        <button 
                                            type="button" 
                                            onclick={() => maxBuildYear = Math.max(1800, maxBuildYear - 1)}
                                            class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-700 font-bold text-xl transition-colors"
                                        >−</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                {:else if step === 5}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Hvar viltu búa?</h2>
                        <p class="text-gray-600 mb-6">Veldu þau póstnúmer sem þú hefur áhuga á.</p>
                        
                        <div class="max-h-[500px] overflow-y-auto border-2 border-gray-100 rounded-xl p-4">
                            {#each zipOptionsGrouped as group}
                                <div class="mb-4">
                                    <button 
                                        onclick={() => toggleZipGroup(group.name)}
                                        class="flex items-center justify-between w-full font-bold text-gray-700 py-2 border-b border-gray-100"
                                    >
                                        {group.name}
                                        <span>{expandedZipGroups[group.name] ? '−' : '+'}</span>
                                    </button>
                                    {#if expandedZipGroups[group.name]}
                                        <div class="mt-2 grid grid-cols-2 gap-2">
                                            {#if group.subgroups}
                                                {#each group.subgroups as sg}
                                                    <div class="col-span-2 mt-2">
                                                        <p class="text-sm font-bold text-gray-500 ml-2">{sg.name}</p>
                                                        <div class="grid grid-cols-2 gap-2 mt-1">
                                                            {#each sg.options as opt}
                                                                <button 
                                                                    onclick={() => toggleZipCode(opt.code)}
                                                                    class="p-2 text-sm rounded-lg border-2 transition-all {selectedZipCodes.includes(opt.code) ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-100 text-gray-600 hover:border-gray-200'}"
                                                                >
                                                                    {opt.code} {opt.name}
                                                                </button>
                                                            {/each}
                                                        </div>
                                                    </div>
                                                {/each}
                                            {:else}
                                                {#each group.options as opt}
                                                    <button 
                                                        onclick={() => toggleZipCode(opt.code)}
                                                        class="p-2 text-sm rounded-lg border-2 transition-all {selectedZipCodes.includes(opt.code) ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-100 text-gray-600 hover:border-gray-200'}"
                                                    >
                                                        {opt.code} {opt.name}
                                                    </button>
                                                {/each}
                                            {/if}
                                        </div>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    </div>

                {:else if step === 6}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Hvers konar eign?</h2>
                        <p class="text-gray-600 mb-6">Veldu þær tegundir sem koma til greina.</p>
                        
                        <div class="grid grid-cols-2 gap-3">
                            <label class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all {einbylishus ? 'border-blue-500 bg-blue-50' : 'border-gray-100'}">
                                <input type="checkbox" bind:checked={einbylishus} class="hidden" />
                                <span class="font-medium text-gray-700">Einbýlishús</span>
                            </label>
                            <label class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all {fjolbylishus ? 'border-blue-500 bg-blue-50' : 'border-gray-100'}">
                                <input type="checkbox" bind:checked={fjolbylishus} class="hidden" />
                                <span class="font-medium text-gray-700">Fjölbýlishús</span>
                            </label>
                            <label class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all {radhus_parhus ? 'border-blue-500 bg-blue-50' : 'border-gray-100'}">
                                <input type="checkbox" checked={radhus_parhus} onchange={(e) => { radhus_parhus = e.target.checked; parhus = e.target.checked; }} class="hidden" />
                                <span class="font-medium text-gray-700">Raðhús / Parhús</span>
                            </label>
                            <label class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all {haed ? 'border-blue-500 bg-blue-50' : 'border-gray-100'}">
                                <input type="checkbox" bind:checked={haed} class="hidden" />
                                <span class="font-medium text-gray-700">Hæð</span>
                            </label>
                            <label class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all {sumarhus ? 'border-blue-500 bg-blue-50' : 'border-gray-100'}">
                                <input type="checkbox" bind:checked={sumarhus} class="hidden" />
                                <span class="font-medium text-gray-700">Sumarhús</span>
                            </label>
                            <label class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all {jord_lod ? 'border-blue-500 bg-blue-50' : 'border-gray-100'}">
                                <input type="checkbox" bind:checked={jord_lod} class="hidden" />
                                <span class="font-medium text-gray-700">Jörð / Lóð</span>
                            </label>
                            <label class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all {atvinnuhusnaedi ? 'border-blue-500 bg-blue-50' : 'border-gray-100'}">
                                <input type="checkbox" bind:checked={atvinnuhusnaedi} class="hidden" />
                                <span class="font-medium text-gray-700">Atvinnuhúsnæði</span>
                            </label>
                        </div>
                    </div>

                {:else if step === 7}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-8">Svalir eða garður?</h2>
                        
                        <div class="flex flex-col gap-3">
                            {#each [
                                { val: 'none', label: 'Skiptir ekki máli' },
                                { val: 'balcony', label: 'Bara svalir' },
                                { val: 'garden', label: 'Bara garður' },
                                { val: 'either', label: 'Annað hvort svalir eða garður' },
                                { val: 'both', label: 'Bæði svalir og garður' }
                            ] as opt}
                                <label class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all {outdoorFilter === opt.val ? 'border-blue-500 bg-blue-50' : 'border-gray-100'}">
                                    <input type="radio" name="outdoor" value={opt.val} bind:group={outdoorFilter} class="hidden" />
                                    <span class="font-medium text-gray-700">{opt.label}</span>
                                </label>
                            {/each}
                        </div>
                    </div>

                {:else if step === 8}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-8">Er bílskúr nauðsynlegur?</h2>
                        
                        <div class="grid grid-cols-2 gap-4">
                            <button 
                                onclick={() => { want_garage = true; nextStep(); }}
                                class="p-8 border-2 rounded-2xl flex flex-col items-center gap-4 transition-all {want_garage === true ? 'border-blue-500 bg-blue-50' : 'border-gray-100 hover:border-gray-200'}"
                            >
                                <span class="text-4xl">🚗</span>
                                <span class="font-bold text-gray-700">Já, endilega</span>
                            </button>
                            <button 
                                onclick={() => { want_garage = false; nextStep(); }}
                                class="p-8 border-2 rounded-2xl flex flex-col items-center gap-4 transition-all {want_garage === false ? 'border-blue-500 bg-blue-50' : 'border-gray-100 hover:border-gray-200'}"
                            >
                                <span class="text-4xl">❌</span>
                                <span class="font-bold text-gray-700">Skiptir ekki máli</span>
                            </button>
                        </div>
                    </div>

                {:else if step === 9}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-6">Frábært! Hér er samantekt:</h2>
                        
                        <div class="bg-gray-50 rounded-xl p-6 space-y-4 mb-8">
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Verðbil</span>
                                <span class="font-bold">{minPrice} - {maxPrice} ISK</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Svefnherbergi</span>
                                <span class="font-bold">{minBedrooms} - {maxBedrooms}</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Byggingarár</span>
                                <span class="font-bold">{minBuildYear} - {maxBuildYear}</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Póstnúmer</span>
                                <div class="text-right">
                                    <p class="font-bold">{selectedZipCodes.length} valin</p>
                                    {#if selectedZipCodes.length > 0}
                                        <p class="text-xs text-gray-400 mt-1">{selectedZipCodes.join(', ')}</p>
                                    {/if}
                                </div>
                            </div>
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Eignategundir</span>
                                <span class="font-bold text-right ml-4">{getSelectedPropertyTypes()}</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Svalir eða garður</span>
                                <span class="font-bold">
                                    {#if outdoorFilter === 'none'}Skiptir ekki máli
                                    {:else if outdoorFilter === 'balcony'}Bara svalir
                                    {:else if outdoorFilter === 'garden'}Bara garður
                                    {:else if outdoorFilter === 'either'}Annað hvort svalir eða garður
                                    {:else if outdoorFilter === 'both'}Bæði svalir og garður
                                    {/if}
                                </span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-500">Bílskúr</span>
                                <span class="font-bold">{want_garage ? 'Já' : 'Skiptir ekki máli'}</span>
                            </div>
                        </div>

                        <button 
                            onclick={() => saveOnboarding(true)}
                            class="w-full bg-green-600 text-white py-4 rounded-xl font-bold text-lg hover:bg-green-700 transition-colors shadow-lg"
                        >
                            Vista og halda áfram
                        </button>
                    </div>
                {/if}

                {#if step > 0 && step < 9}
                    <div class="mt-8 pt-8 border-t border-gray-100 flex justify-between gap-4">
                        <button 
                            onclick={prevStep}
                            class="flex-1 px-6 py-3 border-2 border-gray-100 rounded-xl font-bold text-gray-500 hover:bg-gray-50 transition-colors"
                        >
                            Til baka
                        </button>
                        <button 
                            onclick={nextStep}
                            class="flex-[2] px-6 py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition-colors shadow-md"
                        >
                            Áfram
                        </button>
                    </div>
                {/if}
                
                {#if message}
                    <p class="mt-4 text-center text-red-500 font-medium">{message}</p>
                {/if}
            </div>
        {/if}
    </div>
</div>

{#if showSuccessModal}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-white/40 backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl border border-gray-200 transform transition-all">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-2">Frábært!</h3>
            <p class="text-gray-600 mb-8">
                Þú hefur vistað stillingar. Þú munt fá daglegan tölvupóst með eignum sem passa við þínar kröfur.
            </p>
            <div class="flex flex-col gap-3">
                <button
                    onclick={() => { showSuccessModal = false; window.location.href = '/dashboard'; }}
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
        <div class="bg-white rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl border border-gray-200 transform transition-all">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
            </div>
            <p class="text-gray-600 mb-8 text-lg font-medium">
                Tölvupóstur er í vinnslu, fylgstu vel með!
            </p>
            <button
                onclick={() => { showEmailSentModal = false; window.location.href = '/dashboard'; }}
                class="w-full bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 transition-colors"
            >
                Loka
            </button>
        </div>
    </div>
{/if}
