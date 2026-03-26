<script>
  let email = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let error = $state('');
  let success = $state(false);

  async function handleRegister() {
    error = '';
    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok) {
          success = true;
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
      } else {
          error = data.detail || 'Registration failed';
      }
    } catch (e) {
      error = 'Could not connect to server';
    }
  }
</script>

<div class="flex flex-col items-center justify-center min-h-screen">
  <form onsubmit={(e) => { e.preventDefault(); handleRegister(); }} class="flex flex-col gap-4 p-8 border rounded-lg shadow-md bg-white w-96">
    <h1 class="text-2xl font-bold mb-4">Register</h1>
    
    {#if error}
      <p class="text-red-500 text-sm">{error}</p>
    {/if}

    {#if success}
      <p class="text-green-500 text-sm">Account created! Redirecting to login...</p>
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
    <input 
      type="password" 
      bind:value={confirmPassword} 
      placeholder="Confirm Password" 
      required 
      class="p-2 border rounded"
    />
    <button type="submit" class="bg-green-500 text-white p-2 rounded hover:bg-green-600">
      Sign Up
    </button>

    <p class="text-sm text-center mt-2">
      Already have an account? <a href="/login" class="text-blue-500 hover:underline">Login</a>
    </p>
  </form>
</div>
