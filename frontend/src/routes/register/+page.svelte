<script>
  import { getApiUrl } from '$lib/config';
  
  let email = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let showPassword = $state(false);
  let error = $state('');
  let success = $state(false);

  async function handleRegister() {
    error = '';
    success = false;
    
    if (password !== confirmPassword) {
      error = 'Lykilorðin pössuðu ekki saman';
      return;
    }

    try {
      const res = await fetch(`${getApiUrl()}/register`, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok) {
          success = true;
      } else {
          error = data.detail || 'Nýskráning tókst ekki';
      }
    } catch (e) {
      error = 'Gat ekki tengst þjóni';
    }
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen bg-gray-50">
  <form onsubmit={async (e) => { e.preventDefault(); await handleRegister(); }} class="flex flex-col gap-6 p-12 border rounded-xl shadow-xl bg-white w-[500px]">
    <h1 class="text-3xl font-bold mb-4 text-center">Nýskráning</h1>
    
    {#if error}
      <p class="text-red-500 text-sm p-2 bg-red-50 rounded border border-red-200">{error}</p>
    {/if}

    {#if success}
      <div class="p-8 bg-green-50 border-2 border-green-300 rounded-xl text-green-800 text-center">
        <p class="text-xl font-bold">Skoðaðu tölvupóstinn þinn til þess að staðfesta netfangið þitt!</p>
      </div>
    {:else}
      <div class="flex flex-col gap-1">
        <label for="email" class="text-sm font-medium text-gray-700">Netfang</label>
        <input 
          id="email"
          type="email" 
          bind:value={email} 
          placeholder="netfang@daemi.is" 
          required 
          class="p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>

      <div class="flex flex-col gap-1 relative">
        <label for="password" class="text-sm font-medium text-gray-700">Lykilorð</label>
        <div class="relative">
          <input 
            id="password"
            type={showPassword ? "text" : "password"} 
            bind:value={password} 
            placeholder="••••••••" 
            required 
            class="p-2 border rounded w-full pr-10 focus:ring-2 focus:ring-blue-500 outline-none"
          />
          <button 
            type="button" 
            onclick={() => showPassword = !showPassword}
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
            aria-label={showPassword ? "Fela lykilorð" : "Sýna lykilorð"}
          >
            {#if showPassword}
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.644C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            {/if}
          </button>
        </div>
      </div>

      <div class="flex flex-col gap-1">
        <label for="confirmPassword" class="text-sm font-medium text-gray-700">Staðfesta lykilorð</label>
        <input 
          id="confirmPassword"
          type={showPassword ? "text" : "password"} 
          bind:value={confirmPassword} 
          placeholder="••••••••" 
          required 
          class="p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>

      <button type="submit" class="bg-green-500 text-white p-2 rounded font-semibold hover:bg-green-600 transition-colors shadow-sm mt-2">
        Nýskrá
      </button>
    {/if}

    <p class="text-sm text-center mt-2 text-gray-600">
      Ertu þegar með aðgang? <a href="/login" class="text-blue-500 font-medium hover:underline">Skrá inn</a>
    </p>
  </form>
</div>
