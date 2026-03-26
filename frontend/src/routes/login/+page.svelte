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

<div class="flex flex-col items-center justify-center min-h-screen">
  <form onsubmit={(e) => { e.preventDefault(); handleLogin(); }} class="flex flex-col gap-4 p-8 border rounded-lg shadow-md bg-white">
    <h1 class="text-2xl font-bold mb-4">Login</h1>
    
    {#if error}
      <p class="text-red-500 text-sm">{error}</p>
    {/if}

    <input 
      type="email" 
      bind:value={email} 
      placeholder="Email" 
      required 
      class="p-2 border rounded"
    />
    <input 
      type="password" 
      bind:value={password} 
      placeholder="Password" 
      required 
      class="p-2 border rounded"
    />
    <button type="submit" class="bg-blue-500 text-white p-2 rounded hover:bg-blue-600">
      Login
    </button>

    <p class="text-sm text-center mt-2">
      Don't have an account? <a href="/register" class="text-blue-500 hover:underline">Register</a>
    </p>
  </form>
</div>
