<script lang="ts" generics="T extends string">
	import { getFormFieldClasses } from './formFieldClasses';
	import { ChevronDownIcon } from './icons';

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

	let fieldClasses = $derived(
		getFormFieldClasses(`cursor-pointer appearance-none pr-10 ${className}`)
	);
</script>

<div class="relative">
	<select {id} bind:value aria-label={ariaLabel} class={fieldClasses}>
		{#each options as option (option.value)}
			<option value={option.value}>{option.label}</option>
		{/each}
	</select>
	<ChevronDownIcon
		class="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400 dark:text-slate-500"
	/>
</div>
