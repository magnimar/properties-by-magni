<script>
    import { getApiUrl } from '$lib/config';

    let status = $state('verifying');
    let errorMessage = $state('');
    let countdown = $state(5);

    function getToken() {
        return document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1];
    }

    async function verify() {
        const token = getToken();
        if (!token) {
            window.location.href = '/login';
            return;
        }
        try {
            const res = await fetch(`${getApiUrl()}/me/subscribe/verify`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (!res.ok) {
                status = 'error';
                errorMessage = data.detail || 'Villa við að staðfesta áskrift.';
                return;
            }
            if (data.is_pro) {
                status = 'success';
                startCountdown();
            } else {
                status = 'pending';
            }
        } catch (err) {
            status = 'error';
            errorMessage = 'Tenging við netþjón mistókst.';
        }
    }

    function startCountdown() {
        const interval = setInterval(() => {
            countdown -= 1;
            if (countdown <= 0) {
                clearInterval(interval);
                window.location.href = '/dashboard';
            }
        }, 1000);
    }

    $effect(() => {
        verify();
    });
</script>

<div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
    <div class="max-w-xl w-full bg-white rounded-2xl shadow-xl border p-10 text-center {status === 'success' ? 'border-green-200' : status === 'error' ? 'border-red-200' : 'border-gray-200'}">
        {#if status === 'verifying'}
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-6">
                <svg class="animate-spin h-10 w-10 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </div>
            <h1 class="text-3xl font-extrabold text-gray-900 mb-3">Staðfestir greiðslu…</h1>
            <p class="text-lg text-gray-600">Augnablik, við erum að virkja Pro aðganginn þinn.</p>
        {:else if status === 'success'}
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
                <svg class="h-10 w-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
            </div>
            <h1 class="text-3xl font-extrabold text-gray-900 mb-3">Takk fyrir áskriftina!</h1>
            <p class="text-lg text-gray-600 mb-6">
                Greiðslan þín hefur verið staðfest og Fundvís Pro aðgangurinn þinn er virkur.
            </p>
            <a
                href="/dashboard"
                class="inline-flex justify-center py-3 px-6 border border-transparent rounded-md shadow-sm text-base font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
                Fara í mælaborð
            </a>
            <div class="mt-6 text-sm text-gray-400">
                Þú verður færð/ur sjálfkrafa eftir {countdown} sekúndu{countdown === 1 ? '' : 'r'}…
            </div>
        {:else if status === 'pending'}
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-yellow-100 mb-6">
                <svg class="h-10 w-10 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </div>
            <h1 class="text-3xl font-extrabold text-gray-900 mb-3">Greiðslan er í vinnslu</h1>
            <p class="text-lg text-gray-600 mb-6">
                Við náðum ekki að staðfesta áskriftina strax. Þetta getur tekið nokkrar sekúndur — reyndu að endurnýja síðuna eftir smá stund.
            </p>
            <button
                onclick={() => { status = 'verifying'; verify(); }}
                class="inline-flex justify-center py-3 px-6 border border-transparent rounded-md shadow-sm text-base font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
                Reyna aftur
            </button>
        {:else}
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
                <svg class="h-10 w-10 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            </div>
            <h1 class="text-3xl font-extrabold text-gray-900 mb-3">Villa kom upp</h1>
            <p class="text-lg text-gray-600 mb-6">{errorMessage}</p>
            <a
                href="/upgrade"
                class="inline-flex justify-center py-3 px-6 border border-transparent rounded-md shadow-sm text-base font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
                Til baka
            </a>
        {/if}
    </div>
</div>
