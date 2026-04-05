import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';
import { playwright } from '@vitest/browser-playwright';
import { sveltekit } from '@sveltejs/kit/vite';
import fs from 'fs';
import path from 'path';

const envDir = path.resolve(__dirname, '..');
const envPath = path.join(envDir, '.env');

if (!fs.existsSync(envPath) && !process.env.CI) {
	console.error(`CRITICAL ERROR: Environment file not found at ${envPath}`);
	process.exit(1);
}

export default defineConfig({
	envDir,
	plugins: [tailwindcss(), sveltekit()],
	server: {
		allowedHosts: ['propertiesbymagni.com', 'www.propertiesbymagni.com', 'localhost'],
		host: true, // This allows the tunnel to connect to the local IP
		port: 5000,
		// Commented out to fix local development WebSocket connection
		// hmr: {
		// 	clientPort: 443,
		// 	host: 'propertiesbymagni.com'
		// }
	},
	test: {
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'client',
					browser: {
						enabled: true,
						provider: playwright(),
						instances: [{ browser: 'chromium', headless: true }]
					},
					include: ['src/**/*.svelte.{test,spec}.{js,ts}'],
					exclude: ['src/lib/server/**']
				}
			},

			{
				extends: './vite.config.ts',
				test: {
					name: 'server',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			}
		]
	}
});
