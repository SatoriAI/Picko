/**
 * Shared styling classes for form input elements (Input, TextArea)
 */

const baseClasses =
	'w-full rounded-xl border-[1.5px] px-4 py-3 text-base transition-all focus:outline-none';

const normalClasses = [
	'border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400',
	'focus:border-rose-500 focus:ring-[3px] focus:ring-rose-500/10 focus:bg-white',
	'dark:border-slate-600 dark:bg-slate-700/50 dark:text-white dark:placeholder-slate-500 dark:focus:bg-slate-700'
].join(' ');

const errorClasses = [
	'border-red-400 bg-red-50/50 text-slate-800 placeholder-slate-400',
	'focus:border-red-500 focus:ring-[3px] focus:ring-red-500/10 focus:bg-white',
	'dark:border-red-500/70 dark:bg-red-900/20 dark:text-white dark:placeholder-slate-500 dark:focus:bg-slate-700'
].join(' ');

export function getFormFieldClasses(className: string = '', hasError: boolean = false): string {
	return [baseClasses, hasError ? errorClasses : normalClasses, className]
		.filter(Boolean)
		.join(' ');
}
