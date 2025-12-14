<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		type?: 'button' | 'submit';
		variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
		size?: 'sm' | 'md' | 'lg';
		onclick?: () => void;
		disabled?: boolean;
		class?: string;
		children: Snippet;
	}

	let {
		type = 'button',
		variant = 'primary',
		size = 'md',
		onclick,
		disabled = false,
		class: className = '',
		children
	}: Props = $props();

	const baseClasses =
		'cursor-pointer font-semibold transition-all inline-flex items-center justify-center gap-2';

	const sizeClasses = {
		sm: 'rounded-lg px-3 py-2 text-sm',
		md: 'rounded-xl px-6 py-3.5 text-base',
		lg: 'rounded-xl px-8 py-4 text-lg'
	};

	const variantClasses = {
		primary:
			'w-full bg-gradient-to-r from-orange-400 to-rose-500 text-white shadow-md shadow-rose-500/30 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-rose-500/40 active:translate-y-0 active:shadow-md',
		secondary:
			'w-full border-[1.5px] border-slate-200 bg-transparent text-slate-600 hover:border-rose-500 hover:bg-rose-500/5 hover:text-rose-500 dark:border-slate-600 dark:text-slate-400',
		outline:
			'border-2 border-dashed border-slate-300 text-slate-500 hover:border-orange-500 hover:bg-orange-500/5 hover:text-orange-500 dark:border-slate-600 dark:text-slate-400 dark:hover:text-orange-400',
		ghost:
			'text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200'
	};

	const disabledClasses =
		'cursor-not-allowed opacity-60 hover:translate-y-0 hover:shadow-none active:translate-y-0';

	let computedClasses = $derived(
		[
			baseClasses,
			sizeClasses[size],
			variantClasses[variant],
			disabled ? disabledClasses : '',
			className
		]
			.filter(Boolean)
			.join(' ')
	);
</script>

<button {type} {onclick} {disabled} class={computedClasses}>
	{@render children()}
</button>
