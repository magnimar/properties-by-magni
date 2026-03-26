<script>
    import { onMount } from 'svelte';
    
    let user = $state(null);

    onMount(() => {
        // Simple check for token cookie
        const token = document.cookie.split('; ').find(row => row.startsWith('token='));
        if (!token) {
            window.location.href = '/login';
        }
    });
</script>

<div class="p-8">
    <h1 class="text-3xl font-bold">Dashboard</h1>
    <p class="mt-4">Welcome to your properties dashboard!</p>
    <button 
        onclick={() => { document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"; window.location.href = '/login'; }}
        class="mt-4 bg-red-500 text-white p-2 rounded hover:bg-red-600"
    >
        Logout
    </button>
</div>
