<script lang="ts">
	import { GitHubIcon } from './icons';
</script>

<footer
	class="border-t border-slate-900/5 bg-white/50 px-4 py-8 backdrop-blur-sm transition-colors dark:border-slate-700/50 dark:bg-slate-800/50 sm:px-6"
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
				class="text-sm font-medium text-slate-500 transition-colors hover:text-rose-500 dark:text-slate-400"
			>
				dawidhanrahan.com
			</a>
			<a
				href="https://github.com/dawidhanrahan"
				target="_blank"
				rel="noopener noreferrer"
				class="text-slate-400 transition-colors hover:text-rose-500 dark:text-slate-500"
				aria-label="GitHub"
			>
				<GitHubIcon />
			</a>
		</div>
	</div>
</footer>
