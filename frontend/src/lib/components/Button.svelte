<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
	import type { Snippet } from 'svelte';

	interface Props {
		type?: 'button' | 'submit';
		variant?: 'primary' | 'secondary';
		onclick?: () => void;
		disabled?: boolean;
		class?: string;
		children: Snippet;
	}

	let {
		type = 'button',
		variant = 'primary',
		onclick,
		disabled = false,
		class: className = '',
		children
	}: Props = $props();

	let variantClasses = $derived(
		variant === 'primary'
			? 'bg-gradient-to-r from-orange-400 to-rose-500 text-white shadow-md shadow-rose-500/30 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-rose-500/40 active:translate-y-0 active:shadow-md'
			: $darkMode
				? 'border-[1.5px] border-slate-600 text-slate-400 bg-transparent hover:border-rose-500 hover:bg-rose-500/5 hover:text-rose-500'
				: 'border-[1.5px] border-slate-200 text-slate-600 bg-transparent hover:border-rose-500 hover:bg-rose-500/5 hover:text-rose-500'
	);
</script>

<button
	{type}
	{onclick}
	{disabled}
	class="w-full cursor-pointer rounded-xl px-6 py-3.5 text-base font-semibold transition-all {variantClasses} {disabled
		? 'cursor-not-allowed opacity-60 hover:translate-y-0 hover:shadow-none active:translate-y-0'
		: ''} {className}"
>
	{@render children()}
</button>
