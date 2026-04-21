<script>
    import { getApiUrl } from '$lib/config';
    let termsAccepted = $state(true);
    let selectedPlan = $state('pro');
    let loading = $state(false);
    let errorMessage = $state('');

    function getToken() {
        return document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1];
    }

    async function handleSubscribe() {
        if (!termsAccepted) {
            alert("Þú verður að samþykkja skilmálana.");
            return;
        }
        const token = getToken();
        if (!token) {
            window.location.href = '/login';
            return;
        }

        loading = true;
        errorMessage = '';
        try {
            const res = await fetch(`${getApiUrl()}/me/subscribe`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (!res.ok) {
                errorMessage = data.detail || 'Villa við að hefja áskrift.';
                return;
            }
            window.location.href = data.redirect_url;
        } catch (err) {
            errorMessage = 'Tenging við greiðsluþjónustu mistókst.';
        } finally {
            loading = false;
        }
    }
</script>

<div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
        <div class="text-center mb-12">
            <h1 class="text-4xl font-extrabold text-gray-900 mb-4">Uppfærðu í Fundvís Pro</h1>
            <p class="text-xl text-gray-600">Fáðu fullan aðgang að öllum eiginleikum og gögnum.</p>
        </div>

        <!-- Pricing Table -->
        <div class="bg-white rounded-2xl shadow-xl overflow-hidden mb-12 border border-blue-500">
            <div class="px-6 py-8 sm:p-10 sm:pb-6 relative">
                <div class="absolute top-0 right-0 bg-blue-500 text-white font-bold px-3 py-1 text-sm rounded-bl-lg">
                    Vinsælast
                </div>
                <div>
                    <h3 class="text-2xl leading-6 font-semibold text-gray-900" id="tier-pro">
                        Pro Áskrift
                    </h3>
                    <div class="mt-4 flex items-baseline text-6xl font-extrabold text-gray-900">
                        999 kr.
                        <span class="ml-1 text-2xl font-medium text-gray-500">
                            / mán
                        </span>
                    </div>
                </div>
            </div>
            <div class="px-6 pt-6 pb-8 sm:px-10 bg-gray-50 border-t border-gray-100">
                <ul class="space-y-4">
                    <li class="flex items-start">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <p class="ml-3 text-base text-gray-700">Fullt aðgengi að eins mörgum fasteignum og þú vilt á dag.</p>
                    </li>
                    <li class="flex items-start">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <p class="ml-3 text-base text-gray-700">Ótakmarkaðar eignavaktir</p>
                    </li>
                    <li class="flex items-start">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <p class="ml-3 text-base text-gray-700">Daglegir tölvupóstar</p>
                    </li>
                </ul>
            </div>
        </div>

        <!-- Checkout / Terms Agreement Section -->
        <div class="bg-white p-8 rounded-xl shadow border border-gray-200">
            <h3 class="text-xl font-bold text-gray-900 mb-6">Staðfesting á áskrift</h3>
            
            <div class="flex items-start mb-6">
                <div class="flex items-center h-5">
                    <input
                        id="terms"
                        name="terms"
                        type="checkbox"
                        bind:checked={termsAccepted}
                        class="focus:ring-blue-500 h-5 w-5 text-blue-600 border-gray-300 rounded cursor-pointer"
                    />
                </div>
                <div class="ml-3 text-sm">
                    <label for="terms" class="font-medium text-gray-700 cursor-pointer">
                        Ég samþykki <a href="/compliance/TERMS.md" class="text-blue-600 hover:underline">skilmála (Terms of Service)</a> og <a href="/compliance/PRIVACY.md" class="text-blue-600 hover:underline">persónuverndarstefnu (Privacy Policy)</a>.
                        <br/><br/>
                        Ég skil að ég er að gerast áskrifandi að Fundvís Pro fyrir <strong class="text-gray-900">999 kr. á mánuði</strong> og að áskriftin endurnýjast sjálfkrafa í hverjum mánuði þar til henni er sagt upp. Ég get sagt upp áskriftinni hvenær sem er inni á stillingum aðgangsins míns.
                    </label>
                </div>
            </div>

            <button
                onclick={handleSubscribe}
                disabled={loading}
                class="w-full flex justify-center py-4 px-4 border border-transparent rounded-md shadow-sm text-lg font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
                {loading ? 'Vinsamlegast bíddu…' : 'Greiða 999 kr. & Hefja áskrift'}
            </button>
            {#if errorMessage}
                <div class="mt-3 text-center text-sm text-red-600">{errorMessage}</div>
            {/if}
            <div class="mt-4 text-center text-sm text-gray-500">
               Örugg greiðsla í gegnum Rapyd.
            </div>
        </div>
        
        <div class="mt-8 text-center">
             <a href="/dashboard" class="text-gray-500 hover:text-gray-700 underline">Til baka í mælaborð</a>
        </div>
    </div>
</div>
