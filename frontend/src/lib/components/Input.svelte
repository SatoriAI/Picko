<script lang="ts">
	import { getFormFieldClasses } from './formFieldClasses';

	interface Props {
		id: string;
		type?: 'text' | 'number' | 'date' | 'email' | 'datetime-local';
		value?: string;
		placeholder?: string;
		min?: string;
		readonly?: boolean;
		required?: boolean;
		class?: string;
	}

	let {
		id,
		type = 'text',
		value = $bindable(''),
		placeholder = '',
		min,
		readonly = false,
		required = false,
		class: className = ''
	}: Props = $props();

	let fieldClasses = $derived(getFormFieldClasses(className));
</script>

<input {type} {id} bind:value {placeholder} {min} {readonly} {required} class={fieldClasses} />
