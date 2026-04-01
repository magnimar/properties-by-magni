<script>
    import { onMount } from 'svelte';
    import { getApiUrl } from '$lib/config';
  
    let status = $state('Staðfesti netfang...');
    let error = $state('');
  
    onMount(async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
  
      if (!token) {
          status = '';
          error = 'Enginn staðfestingarkóði fannst í vefslóð.';
          return;
      }
  
      try {
          const res = await fetch(`${getApiUrl()}/verify-email?token=${token}`);
          const data = await res.json();
  
          if (res.ok) {
              // Save token and auto-login
              document.cookie = `token=${data.token}; path=/;`;
              status = 'Netfang staðfest! Verið að skrá þig inn...';
              setTimeout(() => {
                  window.location.href = '/dashboard';
              }, 2000);
          } else {
              status = '';
              error = data.detail || 'Staðfesting mistókst. Hlekkurinn gæti verið ógildur eða útrunninn.';
          }
      } catch (e) {
          status = '';
          error = 'Gat ekki tengst þjóni.';
      }
    });
</script>
  
<div class="flex flex-col items-center justify-center min-h-screen bg-gray-50">
    <div class="p-8 border rounded-lg shadow-md bg-white text-center max-w-md w-full">
        <h1 class="text-2xl font-bold mb-4">Staðfesting netfangs</h1>
        
        {#if error}
            <div class="p-4 bg-red-50 border border-red-200 rounded">
                <p class="text-red-600 font-medium">{error}</p>
                <a href="/login" class="inline-block mt-4 text-blue-500 hover:underline">Fara á innskráningarsíðu</a>
            </div>
        {:else}
            <div class="p-4 bg-green-50 border border-green-200 rounded">
                <p class="text-green-700 font-medium">{status}</p>
                {#if status.includes('staðfest')}
                    <p class="text-sm text-green-600 mt-2">Komið, beini þér á innskráningarsíðu...</p>
                {:else}
                    <div class="mt-4 animate-pulse flex justify-center">
                        <div class="h-6 w-6 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>
