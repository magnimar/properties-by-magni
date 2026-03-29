<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="absolute top-4 left-4 z-50">
	<a href="/" class="block hover:opacity-80 transition-opacity">
		<img src="/logo/logo.png" alt="Properties by Magni Logo" class="h-12 w-auto" />
	</a>
</div>

{@render children()}
