<script>
    import { onMount } from 'svelte';
    import { getApiUrl } from '$lib/config';
    
    let user = $state(null);
    let minPrice = $state('0');
    let maxPrice = $state('0');
    let minBedrooms = $state(1);
    let maxBedrooms = $state(1);
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
    let loading = $state(true);
    let showZipDropdown = $state(false);
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
            
            savePreferences();
        }
    }

    function removeStreet(street) {
        ignoredStreets = ignoredStreets.filter(s => s !== street);
        // Auto-save to the database
        savePreferences();
    }

    const zipOptionsGrouped = [
        {
            name: "Höfuðborgarsvæðið",
            subgroups: [
                {
                    name: "Reykjavík",
                    options: [
                        { code: "101", name: "Reykjavík" }, { code: "102", name: "Reykjavík" },
                        { code: "103", name: "Reykjavík" }, { code: "104", name: "Reykjavík" },
                        { code: "105", name: "Reykjavík" }, { code: "107", name: "Reykjavík" },
                        { code: "108", name: "Reykjavík" }, { code: "109", name: "Reykjavík" },
                        { code: "110", name: "Reykjavík" }, { code: "111", name: "Reykjavík" },
                        { code: "112", name: "Reykjavík" }, { code: "113", name: "Reykjavík" },
                        { code: "116", name: "Reykjavík" }, { code: "161", name: "Reykjavík" },
                        { code: "162", name: "Reykjavík" }
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
        "Suðurland": false,
        "Suðurnes": false
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

    function formatNumber(val) {
        if (!val && val !== 0) return '';
        let num = String(val).replace(/,/g, '').replace(/\D/g, '');
        return num ? parseInt(num, 10).toLocaleString('en-US') : '';
    }

    function parseNumber(val) {
        if (!val) return 0;
        return parseInt(String(val).replace(/,/g, ''), 10) || 0;
    }

    function getToken() {
        return document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1];
    }

    async function fetchProfile() {
        const token = getToken();
        if (!token) {
            window.location.href = '/login';
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
                minPrice = formatNumber(user.min_price || 0);
                maxPrice = formatNumber(user.max_price || 0);
                minBedrooms = user.min_bedrooms || 1;
                maxBedrooms = user.max_bedrooms || 1;
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
                window.location.href = '/login';
            }
        } catch (e) {
            message = 'Error connecting to server';
        } finally {
            loading = false;
        }
    }

    async function savePreferences() {
        const token = getToken();
        message = 'Saving...';
        
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
                    want_garage: want_garage
                })
            });

            if (res.ok) {
                message = 'Preferences saved successfully!';
                setTimeout(() => { message = ''; }, 3000);
            } else {
                message = 'Failed to save preferences.';
            }
        } catch (e) {
            message = 'Error saving preferences.';
        }
    }

    onMount(() => {
        fetchProfile();

        if (!window.google) {
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places&loading=async`;
            script.async = true;
            script.defer = true;
            document.head.appendChild(script);
        }
    });
</script>

<div class="p-8 max-w-2xl mx-auto">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">Properties Dashboard</h1>
        <button 
            onclick={() => { document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"; window.location.href = '/login'; }}
            class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
        >
            Logout
        </button>
    </div>

    {#if loading}
        <p>Loading your profile...</p>
    {:else if user}
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h2 class="text-xl font-semibold mb-4">Search Preferences</h2>
            <p class="text-sm text-gray-600 mb-6">Set your price and bedroom range to filter property alerts.</p>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                    <label for="minPrice" class="block text-sm font-medium text-gray-700 mb-1">Minimum Price (ISK)</label>
                    <input 
                        type="text" 
                        inputmode="numeric"
                        id="minPrice" 
                        value={minPrice}
                        oninput={(e) => minPrice = formatNumber(e.target.value)}
                        class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
                <div>
                    <label for="maxPrice" class="block text-sm font-medium text-gray-700 mb-1">Maximum Price (ISK)</label>
                    <input 
                        type="text" 
                        inputmode="numeric"
                        id="maxPrice" 
                        value={maxPrice}
                        oninput={(e) => maxPrice = formatNumber(e.target.value)}
                        class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
                <div>
                    <label for="minBedrooms" class="block text-sm font-medium text-gray-700 mb-1">Minimum Bedrooms</label>
                    <input 
                        type="number" 
                        id="minBedrooms" 
                        bind:value={minBedrooms}
                        class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
                <div>
                    <label for="maxBedrooms" class="block text-sm font-medium text-gray-700 mb-1">Maximum Bedrooms</label>
                    <input 
                        type="number" 
                        id="maxBedrooms" 
                        bind:value={maxBedrooms}
                        class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                </div>
            </div>

            <div class="mb-6 relative">
                <label class="block text-sm font-medium text-gray-700 mb-2">Zip Codes</label>
                <div class="relative">
                    <button 
                        type="button"
                        onclick={() => showZipDropdown = !showZipDropdown}
                        class="w-full text-left p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none bg-white flex justify-between items-center"
                    >
                        <span>
                            {selectedZipCodes.length > 0 
                                ? selectedZipCodes.map(code => {
                                    const opt = zipOptions.find(o => o.code === String(code));
                                    return opt ? `${opt.code} ${opt.name}` : code;
                                }).join(', ') 
                                : 'Select Zip Codes...'}
                        </span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                    
                    {#if showZipDropdown}
                        <div class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded shadow-lg">
                            <ul class="max-h-80 overflow-auto py-1">
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
            </div>

            <div class="mb-6">
                <label for="street-search" class="block text-sm font-medium text-gray-700 mb-2">Ignored Streets</label>
                <div class="mb-3 flex items-center gap-2">
                    <div class="w-full flex-grow" use:setupPlaces>
                        <!-- Google Maps PlaceAutocompleteElement will inject here -->
                    </div>
                    <button 
                        type="button"
                        onclick={addPendingStreet}
                        disabled={!pendingStreetName}
                        class="bg-blue-600 text-white px-4 py-2 h-[42px] rounded font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
                    >
                        Add
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
                                    title="Remove street"
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

            <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">Property Types</label>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={einbylishus} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Einbýlishús (Single-family home)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={fjolbylishus} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Fjölbýlishús (Apartment building)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={atvinnuhusnaedi} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Atvinnuhúsnæði (Commercial)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={radhus_parhus} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Raðhús/Parhús (Terraced/Semi-detached)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={sumarhus} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Sumarhús (Summer house)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={parhus} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Parhús (Semi-detached)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={jord_lod} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Jörð/Lóð (Land/Lot)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={haed} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Hæð (Floor/Story)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={hesthus} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Hesthús (Stable)</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={oflokkad} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Óflokkað (Unclassified)</span>
                    </label>
                </div>
            </div>

            <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">Svalir og garður</label>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                    <label class="flex items-center cursor-pointer">
                        <input type="radio" name="outdoorFilter" value="balcony" bind:group={outdoorFilter} class="form-radio h-5 w-5 text-blue-600 border-gray-300 focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Bara svalir</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="radio" name="outdoorFilter" value="garden" bind:group={outdoorFilter} class="form-radio h-5 w-5 text-blue-600 border-gray-300 focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Bara garður</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="radio" name="outdoorFilter" value="either" bind:group={outdoorFilter} class="form-radio h-5 w-5 text-blue-600 border-gray-300 focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Annað hvort</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="radio" name="outdoorFilter" value="both" bind:group={outdoorFilter} class="form-radio h-5 w-5 text-blue-600 border-gray-300 focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Bæði</span>
                    </label>
                    <label class="flex items-center cursor-pointer">
                        <input type="radio" name="outdoorFilter" value="none" bind:group={outdoorFilter} class="form-radio h-5 w-5 text-blue-600 border-gray-300 focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Skiptir ekki máli</span>
                    </label>
                </div>

                <label class="block text-sm font-medium text-gray-700 mb-2">Annað</label>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" bind:checked={want_garage} class="form-checkbox h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                        <span class="ml-3 text-sm font-medium text-gray-700">Bílskúr (Garage)</span>
                    </label>
                </div>
            </div>

            <div class="flex items-center gap-4">
                <button 
                    onclick={savePreferences}
                    class="bg-blue-600 text-white px-6 py-2 rounded font-medium hover:bg-blue-700 transition-colors"
                >
                    Save Preferences
                </button>
                
                {#if message}
                    <span class="text-sm font-medium {message.includes('Error') || message.includes('Failed') ? 'text-red-500' : 'text-green-600'}">
                        {message}
                    </span>
                {/if}
            </div>
        </div>

        <div class="mt-8">
            <p class="text-gray-500 italic">Signed in as: {user.email}</p>
        </div>
    {/if}
</div>
