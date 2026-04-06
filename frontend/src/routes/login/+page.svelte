<script>
  import { getApiUrl } from '$lib/config';
  
  let email = $state('');
  let password = $state('');
  let error = $state('');

  async function handleLogin() {
    error = '';
    try {
      const res = await fetch(`${getApiUrl()}/login`, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok) {
          // Save token and redirect
          document.cookie = `token=${data.token}; path=/;`;
          window.location.href = '/dashboard';
      } else {
          error = data.detail || 'Login failed';
      }
    } catch (e) {
      error = 'Could not connect to server';
    }
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen bg-gray-50">
  <div class="fixed top-0 left-0 pt-10 pl-6 md:pl-10 lg:pt-12 z-50">
    <a href="/home" class="flex items-center hover:opacity-90 transition-opacity">
        <span class="font-bold text-4xl md:text-5xl tracking-tight text-blue-500 mt-2 ml-1" style="letter-spacing: -0.02em;">Fundvís</span>
    </a>
  </div>
  <form onsubmit={(e) => { e.preventDefault(); handleLogin(); }} class="flex flex-col gap-6 p-12 border rounded-xl shadow-xl bg-white w-[500px]">
    <h1 class="text-3xl font-bold mb-4 text-center">Innskráning</h1>
    
    {#if error}
      <p class="text-red-500 text-sm">{error}</p>
    {/if}

    <input 
      type="email" 
      bind:value={email} 
      placeholder="Netfang" 
      required 
      class="p-2 border rounded"
    />
    <input 
      type="password" 
      bind:value={password} 
      placeholder="Lykilorð" 
      required 
      class="p-2 border rounded"
    />
    <button type="submit" class="bg-blue-500 text-white p-2 rounded hover:bg-blue-600">
      Innskráning
    </button>

    <div class="text-sm text-center mt-2 flex flex-col gap-2">
      <a href="/forgot-password" class="text-blue-500 hover:underline">Gleymt lykilorð?</a>
      <p>
        Ertu ekki með aðgang? <a href="/register" class="text-blue-500 hover:underline">Nýskráning</a>
      </p>
    </div>
  </form>
</div>
