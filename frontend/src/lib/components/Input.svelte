<script lang="ts">
	import { getFormFieldClasses } from './formFieldClasses';

	interface Props {
		id: string;
		type?: 'text' | 'number' | 'date' | 'email';
		value?: string;
		placeholder?: string;
		min?: string;
		class?: string;
	}

	let {
		id,
		type = 'text',
		value = $bindable(''),
		placeholder = '',
		min,
		class: className = ''
	}: Props = $props();

	let fieldClasses = $derived(getFormFieldClasses(className));
</script>

<input {type} {id} bind:value {placeholder} {min} class={fieldClasses} />
