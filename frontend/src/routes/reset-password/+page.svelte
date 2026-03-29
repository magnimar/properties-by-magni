<script>
  import { getApiUrl } from '$lib/config';
  import { onMount } from 'svelte';
  import { page } from '$app/state';

  let token = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');
  let message = $state('');
  let error = $state('');
  let loading = $state(false);

  onMount(() => {
    token = page.url.searchParams.get('token') || '';
    if (!token) {
      error = 'Invalid reset link. Token is missing.';
    }
  });

  async function handleResetPassword() {
    if (newPassword !== confirmPassword) {
      error = 'Lykilorðin stemma ekki';
      return;
    }

    if (newPassword.length < 8) {
      error = 'Lykilorðið verður að vera að minnsta kosti 8 stafir';
      return;
    }

    error = '';
    message = '';
    loading = true;
    try {
      const res = await fetch(`${getApiUrl()}/reset-password`, {
        method: 'POST',
        body: JSON.stringify({ token, new_password: newPassword }),
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok) {
          message = 'Lykilorðinu hefur verið breytt. Þú getur nú skráð þig inn með nýja lykilorðinu.';
          setTimeout(() => {
            window.location.href = '/login';
          }, 3000);
      } else {
          error = data.detail || 'Eitthvað fór úrskeiðis';
      }
    } catch (e) {
      error = 'Ekki náðist samband við þjóninn';
    } finally {
      loading = false;
    }
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen">
  <form onsubmit={(e) => { e.preventDefault(); handleResetPassword(); }} class="flex flex-col gap-4 p-8 border rounded-lg shadow-md bg-white max-w-md w-full">
    <h1 class="text-2xl font-bold mb-4">Endurstilla lykilorð</h1>
    
    {#if error}
      <p class="text-red-500 text-sm">{error}</p>
    {/if}

    {#if message}
      <p class="text-green-600 text-sm font-medium">{message}</p>
    {/if}

    {#if token && !message}
        <input 
          type="password" 
          bind:value={newPassword} 
          placeholder="Nýtt lykilorð" 
          required 
          class="p-2 border rounded"
        />
        <input 
          type="password" 
          bind:value={confirmPassword} 
          placeholder="Staðfesta nýtt lykilorð" 
          required 
          class="p-2 border rounded"
        />
        <button 
          type="submit" 
          disabled={loading}
          class="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:bg-blue-300"
        >
          {loading ? 'Breyta...' : 'Breyta lykilorði'}
        </button>
    {/if}

    <div class="text-sm text-center mt-2">
      <a href="/login" class="text-blue-500 hover:underline">Aftur í innskráningu</a>
    </div>
  </form>
</div>
