<script lang="ts" generics="T extends string">
	interface Props {
		id: string;
		value?: T;
		options: Array<{ value: T; label: string }>;
		class?: string;
		'aria-label'?: string;
	}

	let {
		id,
		value = $bindable() as T,
		options,
		class: className = '',
		'aria-label': ariaLabel
	}: Props = $props();

	// Separate width/layout classes from styling classes
	// Width classes go to wrapper, other classes go to select
	function getWrapperClasses() {
		const classes = className.split(' ');
		const widthClasses = classes.filter(
			(c) => c.startsWith('w-') || c.startsWith('flex-') || c === 'flex-1'
		);
		return ['relative', ...widthClasses].filter(Boolean).join(' ');
	}

	function getSelectOnlyClasses() {
		const classes = className.split(' ');
		return classes
			.filter((c) => !c.startsWith('w-') && !c.startsWith('flex-') && c !== 'flex-1')
			.join(' ');
	}

	let wrapperClasses = $derived(getWrapperClasses());
	let selectOnlyClasses = $derived(getSelectOnlyClasses());
</script>

<div class={wrapperClasses}>
	<select
		{id}
		bind:value
		aria-label={ariaLabel}
		class="w-full cursor-pointer rounded-xl border-[1.5px] py-3 pl-3 pr-9 text-base font-medium transition-all focus:border-rose-500 focus:ring-[3px] focus:ring-rose-500/10 focus:outline-none border-slate-200 bg-slate-50 text-slate-800 focus:bg-white dark:border-slate-600 dark:bg-slate-700/50 dark:text-white dark:focus:bg-slate-700 {selectOnlyClasses}"
	>
		{#each options as option (option.value)}
			<option value={option.value}>{option.label}</option>
		{/each}
	</select>
	<!-- Custom dropdown arrow -->
	<div
		class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500"
	>
		<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
			<path stroke-linecap="round" stroke-linejoin="round" d="M6 9l6 6 6-6" />
		</svg>
	</div>
</div>

<style>
	/* Hide native select arrow across browsers */
	select {
		-webkit-appearance: none;
		-moz-appearance: none;
		appearance: none;
		background-image: none;
	}

	/* Remove IE arrow */
	select::-ms-expand {
		display: none;
	}
</style>
