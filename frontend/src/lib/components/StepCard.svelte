<script lang="ts">
	import { darkMode } from '$lib/stores/theme';

	interface Props {
		step: number;
		title: string;
		description: string;
		color: 'emerald' | 'amber' | 'rose';
	}

	let { step, title, description, color }: Props = $props();

	const colorClasses = {
		emerald: 'from-emerald-400 to-emerald-500 shadow-emerald-400/35',
		amber: 'from-amber-400 to-orange-500 shadow-orange-400/35',
		rose: 'from-rose-400 to-rose-500 shadow-rose-400/35'
	};
</script>

<article
	class="flex items-start gap-4 rounded-2xl border p-5 shadow-sm transition-all hover:shadow-md {$darkMode
		? 'border-slate-700/50 bg-slate-800/50'
		: 'border-slate-900/5 bg-white'}"
>
	<div
		class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br text-lg font-bold text-white shadow-md {colorClasses[
			color
		]}"
	>
		{step}
	</div>
	<div>
		<h3 class="mb-1 text-base font-semibold {$darkMode ? 'text-white' : 'text-slate-800'}">
			{title}
		</h3>
		<p class="text-sm leading-relaxed {$darkMode ? 'text-slate-400' : 'text-slate-500'}">
			{description}
		</p>
	</div>
</article>
