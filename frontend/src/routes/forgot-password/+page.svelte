<script>
  import { getApiUrl } from '$lib/config';
  
  let email = $state('');
  let message = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleForgotPassword() {
    error = '';
    message = '';
    loading = true;
    try {
      const res = await fetch(`${getApiUrl()}/forgot-password`, {
        method: 'POST',
        body: JSON.stringify({ email }),
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok) {
          message = data.message;
      } else {
          error = data.detail || 'Something went wrong';
      }
    } catch (e) {
      error = 'Could not connect to server';
    } finally {
      loading = false;
    }
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen">
  <form onsubmit={(e) => { e.preventDefault(); handleForgotPassword(); }} class="flex flex-col gap-4 p-8 border rounded-lg shadow-md bg-white max-w-md w-full">
    <h1 class="text-2xl font-bold mb-4">Gleymt lykilorð</h1>
    
    <p class="text-gray-600 text-sm mb-2">
      Sláðu inn netfangið þitt og við sendum þér hlekk til að endurstilla lykilorðið.
    </p>

    {#if error}
      <p class="text-red-500 text-sm">{error}</p>
    {/if}

    {#if message}
      <p class="text-green-600 text-sm font-medium">{message}</p>
    {/if}

    <input 
      type="email" 
      bind:value={email} 
      placeholder="Netfang" 
      required 
      class="p-2 border rounded"
    />
    <button 
      type="submit" 
      disabled={loading}
      class="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:bg-blue-300"
    >
      {loading ? 'Sendir...' : 'Senda hlekk'}
    </button>

    <div class="text-sm text-center mt-2">
      <a href="/login" class="text-blue-500 hover:underline">Aftur í innskráningu</a>
    </div>
  </form>
</div>
