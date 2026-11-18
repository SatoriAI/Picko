import { paraglideVitePlugin } from '@inlang/paraglide-js';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';
import { GUIDE_IDS, GUIDE_PATHS, guideRoute } from './src/lib/guides/paths';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit(),
		paraglideVitePlugin({
			project: './project.inlang',
			outdir: './src/lib/paraglide',
			// The homepage and the guides have a URL per language, so search engines can index each one; `/` redirects to
			// the visitor's language. Token pages keep one URL and use the explicit choice (cookie), then the browser
			// language.
			strategy: ['url', 'cookie', 'globalVariable', 'preferredLanguage', 'baseLocale'],
			urlPatterns: [
				{
					pattern: '/',
					localized: [
						['pl', '/pl'],
						['en', '/en']
					]
				},
				...GUIDE_IDS.map((id) => ({
					pattern: guideRoute(id),
					localized: [
						['pl', GUIDE_PATHS[id].pl],
						['en', GUIDE_PATHS[id].en]
					] as [string, string][]
				}))
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
