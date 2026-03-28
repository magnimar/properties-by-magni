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
    let message = $state('');
    let loading = $state(true);
    let showZipDropdown = $state(false);
    let pendingStreetName = $state('');

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
                        await place.fetchFields({ fields: ['displayName', 'formattedAddress'] });
                        const streetName = place.displayName ? place.displayName.text : place.formattedAddress;
                        
                        if (streetName) {
                            pendingStreetName = streetName;
                        }
                    } catch (err) {
                        console.error("Error fetching place details:", err);
                    }
                });

                autocompleteEl.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') e.preventDefault();
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

    function addPendingStreet() {
        if (pendingStreetName && !ignoredStreets.includes(pendingStreetName)) {
            ignoredStreets = [...ignoredStreets, pendingStreetName];
            pendingStreetName = '';
            
            // Clear the input in the shadow DOM
            const autocompleteEl = document.getElementById('street-search');
            if (autocompleteEl) {
                // @ts-ignore
                autocompleteEl.value = '';
                // @ts-ignore
                autocompleteEl.inputValue = '';
            }
            
            // Auto-save to the database
            savePreferences();
        }
    }

    function removeStreet(street) {
        ignoredStreets = ignoredStreets.filter(s => s !== street);
        // Auto-save to the database
        savePreferences();
    }

    const zipOptions = [
        "104 Reykjavík",
        "105 Reykjavík",
        "107 Reykjavík"
    ];

    function toggleZipCode(zip) {
        if (selectedZipCodes.includes(zip)) {
            selectedZipCodes = selectedZipCodes.filter(z => z !== zip);
        } else {
            selectedZipCodes = [...selectedZipCodes, zip];
        }
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
                selectedZipCodes = user.zip_codes || [];
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
                    oflokkad: oflokkad
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
                            {selectedZipCodes.length > 0 ? selectedZipCodes.join(', ') : 'Select Zip Codes...'}
                        </span>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                    
                    {#if showZipDropdown}
                        <div class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded shadow-lg">
                            <ul class="max-h-60 overflow-auto py-1">
                                {#each zipOptions as zip}
                                    <li>
                                        <label class="flex items-center px-4 py-2 hover:bg-gray-100 cursor-pointer">
                                            <input 
                                                type="checkbox" 
                                                class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                                checked={selectedZipCodes.includes(zip)}
                                                onchange={() => toggleZipCode(zip)}
                                            />
                                            <span class="ml-3 text-sm text-gray-700">{zip}</span>
                                        </label>
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
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
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
