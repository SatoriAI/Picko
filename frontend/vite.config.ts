import { paraglideVitePlugin } from '@inlang/paraglide-js';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit(),
		paraglideVitePlugin({
			project: './project.inlang',
			outdir: './src/lib/paraglide',
			// Only the homepage has a URL per language, so search engines can index each one; `/` redirects to the
			// visitor's language. Token pages keep one URL and use the explicit choice (cookie), then the browser language.
			strategy: ['url', 'cookie', 'globalVariable', 'preferredLanguage', 'baseLocale'],
			urlPatterns: [
				{
					pattern: '/',
					localized: [
						['pl', '/pl'],
						['en', '/en']
					]
				}
			]
		})
	],
	test: {
		expect: { requireAssertions: true },
		projects: [
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
