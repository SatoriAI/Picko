<script lang="ts">
	import { getFormFieldClasses } from './formFieldClasses';

	interface Props {
		id: string;
		value?: string;
		placeholder?: string;
		rows?: number;
		error?: boolean;
		class?: string;
	}

	let {
		id,
		value = $bindable(''),
		placeholder = '',
		rows = 3,
		error = false,
		class: className = ''
	}: Props = $props();

	let fieldClasses = $derived(getFormFieldClasses(`resize-none ${className}`, error));
</script>

<textarea
	{id}
	bind:value
	{placeholder}
	{rows}
	aria-invalid={error || undefined}
	class={fieldClasses}
></textarea>
