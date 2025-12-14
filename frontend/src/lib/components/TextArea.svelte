<script lang="ts">
	import { getFormFieldClasses } from './formFieldClasses';

	interface Props {
		id: string;
		value?: string;
		placeholder?: string;
		rows?: number;
		class?: string;
	}

	let {
		id,
		value = $bindable(''),
		placeholder = '',
		rows = 3,
		class: className = ''
	}: Props = $props();

	let fieldClasses = $derived(getFormFieldClasses(`resize-none ${className}`));
</script>

<textarea {id} bind:value {placeholder} {rows} class={fieldClasses}></textarea>
