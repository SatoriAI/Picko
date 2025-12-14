<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import { GitHubIcon } from './icons';
</script>

<footer
	class="border-t px-4 py-8 backdrop-blur-sm transition-colors sm:px-6 {$darkMode
		? 'border-slate-700/50 bg-slate-800/50'
		: 'border-slate-900/5 bg-white/50'}"
>
	<div
		class="mx-auto flex max-w-5xl flex-col items-center gap-4 text-center sm:flex-row sm:justify-between sm:text-left"
	>
		<p class="text-sm text-slate-500">
			© {new Date().getFullYear()} Created by Dawid Hanrahan
		</p>
		<div class="flex items-center gap-5">
			<a
				href="https://dawidhanrahan.com"
				target="_blank"
				rel="noopener noreferrer"
				class="text-sm font-medium transition-colors hover:text-rose-500 {$darkMode
					? 'text-slate-400'
					: 'text-slate-500'}"
			>
				dawidhanrahan.com
			</a>
			<a
				href="https://github.com/dawidhanrahan"
				target="_blank"
				rel="noopener noreferrer"
				class="transition-colors hover:text-rose-500 {$darkMode
					? 'text-slate-500'
					: 'text-slate-400'}"
				aria-label="GitHub"
			>
				<GitHubIcon />
			</a>
		</div>
	</div>
</footer>
