<script lang="ts">
	import { darkMode } from '$lib/stores/theme';
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

	let fieldClasses = $derived(getFormFieldClasses($darkMode, className));
</script>

<input {type} {id} bind:value {placeholder} {min} class={fieldClasses} />
