<script>
    import { onMount } from 'svelte';
    
    onMount(() => {
        const token = document.cookie.split('; ').find(row => row.startsWith('token='));
        if (token) {
            window.location.href = '/dashboard';
        } else {
            window.location.href = '/login';
        }
    });
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-50">
  <p class="text-lg text-gray-500 animate-pulse">Redirecting...</p>
</div>
