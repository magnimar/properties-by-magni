<script>
    import { onMount } from 'svelte';
    import { getApiUrl } from '$lib/config';
  
    let status = $state('Verifying your email...');
    let error = $state('');
  
    onMount(async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
  
      if (!token) {
          status = '';
          error = 'No verification token provided in the URL.';
          return;
      }
  
      try {
          const res = await fetch(`${getApiUrl()}/verify-email?token=${token}`);
          const data = await res.json();
  
          if (res.ok) {
              status = 'Email verified successfully! You can now log in.';
              setTimeout(() => {
                  window.location.href = '/login';
              }, 3000);
          } else {
              status = '';
              error = data.detail || 'Verification failed. The link might be invalid or expired.';
          }
      } catch (e) {
          status = '';
          error = 'Could not connect to the server.';
      }
    });
</script>
  
<div class="flex flex-col items-center justify-center min-h-screen bg-gray-50">
    <div class="p-8 border rounded-lg shadow-md bg-white text-center max-w-md w-full">
        <h1 class="text-2xl font-bold mb-4">Email Verification</h1>
        
        {#if error}
            <div class="p-4 bg-red-50 border border-red-200 rounded">
                <p class="text-red-600 font-medium">{error}</p>
                <a href="/login" class="inline-block mt-4 text-blue-500 hover:underline">Go to Login</a>
            </div>
        {:else}
            <div class="p-4 bg-green-50 border border-green-200 rounded">
                <p class="text-green-700 font-medium">{status}</p>
                {#if status.includes('successfully')}
                    <p class="text-sm text-green-600 mt-2">Redirecting to login...</p>
                {:else}
                    <div class="mt-4 animate-pulse flex justify-center">
                        <div class="h-6 w-6 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>
