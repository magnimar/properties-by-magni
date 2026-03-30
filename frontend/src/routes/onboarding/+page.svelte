<script>
    import { onMount } from 'svelte';
    import { getApiUrl } from '$lib/config';
    
    let user = $state(null);
    let step = $state(0); // 0: Intro, 1: Min Price, 2: Max Price, 3: Bedrooms, 4: Zip Codes, 5: Property Types, 6: Outdoor, 7: Garage, 8: Review
    
    let minPrice = $state('0');
    let maxPrice = $state('0');
    let minBedrooms = $state(1);
    let maxBedrooms = $state(1);
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
                    window.location.href = '/dashboard';
                }
            } else {
                message = 'Failed to save progress.';
            }
        } catch (e) {
            message = 'Error saving preferences.';
        }
    }

    function nextStep() {
        if (step < 8) {
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
            name: "Landsbyggðin",
            options: [
                { code: "300", name: "Akranes" }, { code: "600", name: "Akureyri" },
                { code: "800", name: "Selfoss" }, { code: "230", name: "Reykjanesbær" }
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
                    style="width: {(step / 8) * 100}%"
                ></div>
            </div>

            <div class="p-8 md:p-12">
                {#if step === 0}
                    <div class="text-center">
                        <h1 class="text-3xl font-bold text-gray-900 mb-4">Velkomin(n) í Magni!</h1>
                        <p class="text-lg text-gray-600 mb-8">Við skulum byrja á því að stilla leitarskilyrðin þín svo þú fáir aðeins eignir sem henta þér.</p>
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
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Svefnherbergi</h2>
                        <p class="text-gray-600 mb-8">Hversu mörg herbergi þarftu?</p>
                        <div class="grid grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-bold text-gray-700 mb-2">Lágmark</label>
                                <input 
                                    type="number" 
                                    bind:value={minBedrooms}
                                    min="1"
                                    class="w-full p-4 text-xl border-2 border-gray-200 rounded-xl focus:border-blue-500 outline-none"
                                />
                            </div>
                            <div>
                                <label class="block text-sm font-bold text-gray-700 mb-2">Hámark</label>
                                <input 
                                    type="number" 
                                    bind:value={maxBedrooms}
                                    min="1"
                                    class="w-full p-4 text-xl border-2 border-gray-200 rounded-xl focus:border-blue-500 outline-none"
                                />
                            </div>
                        </div>
                    </div>

                {:else if step === 4}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Hvar viltu búa?</h2>
                        <p class="text-gray-600 mb-6">Veldu þau póstnúmer sem þú hefur áhuga á.</p>
                        
                        <div class="max-h-64 overflow-y-auto border-2 border-gray-100 rounded-xl p-4">
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
                                                                    {opt.code}
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

                {:else if step === 5}
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

                {:else if step === 6}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Svalir eða garður?</h2>
                        <p class="text-gray-600 mb-8">Skiptir útivistarsvæði máli?</p>
                        
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

                {:else if step === 7}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Bílskúr?</h2>
                        <p class="text-gray-600 mb-8">Er bílskúr nauðsynlegur?</p>
                        
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

                {:else if step === 8}
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-6">Frábært! Hér er samantekt:</h2>
                        
                        <div class="bg-gray-50 rounded-xl p-6 space-y-4 mb-8">
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Verðbil</span>
                                <span class="font-bold">{minPrice} - {maxPrice} ISK</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Herbergi</span>
                                <span class="font-bold">{minBedrooms} - {maxBedrooms}</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-200 pb-2">
                                <span class="text-gray-500">Póstnúmer</span>
                                <span class="font-bold">{selectedZipCodes.length} valin</span>
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
                            Vista og halda áfram á mælaborð
                        </button>
                    </div>
                {/if}

                {#if step > 0 && step < 8}
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
