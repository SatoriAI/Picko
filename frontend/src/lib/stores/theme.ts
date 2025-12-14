import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createThemeStore() {
	const storedTheme = browser ? localStorage.getItem('darkMode') === 'true' : false;
	const { subscribe, set, update } = writable(storedTheme);

	return {
		subscribe,
		toggle: () =>
			update((value) => {
				const newValue = !value;
				if (browser) {
					localStorage.setItem('darkMode', String(newValue));
				}
				return newValue;
			}),
		set: (value: boolean) => {
			if (browser) {
				localStorage.setItem('darkMode', String(value));
			}
			set(value);
		}
	};
}

export const darkMode = createThemeStore();
