<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		variant?: 'default' | 'success' | 'primary';
		size?: 'sm' | 'md';
		onclick?: () => void;
		disabled?: boolean;
		class?: string;
		children: Snippet;
	}

	let {
		variant = 'default',
		size = 'md',
		onclick,
		disabled = false,
		class: className = '',
		children
	}: Props = $props();

	const baseClasses =
		'cursor-pointer font-medium transition-all inline-flex items-center justify-center gap-2';

	const sizeClasses = {
		sm: 'rounded-lg px-3 py-2 text-xs',
		md: 'rounded-lg px-3 py-2 text-sm'
	};

	const variantClasses = {
		default:
			'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600',
		success: 'bg-emerald-500 text-white shadow-md shadow-emerald-500/25',
		primary: 'bg-orange-500 text-white hover:bg-orange-600'
	};

	const disabledClasses = 'cursor-not-allowed opacity-60';

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

<button type="button" {onclick} {disabled} class={computedClasses}>
	{@render children()}
</button>
