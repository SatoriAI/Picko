/**
 * Shared styling classes for form input elements (Input, TextArea)
 */
export function getFormFieldClasses(className: string = ''): string {
	return [
		'w-full rounded-xl border-[1.5px] px-4 py-3 text-base transition-all focus:border-rose-500 focus:ring-[3px] focus:ring-rose-500/10 focus:outline-none',
		'border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400 focus:bg-white',
		'dark:border-slate-600 dark:bg-slate-700/50 dark:text-white dark:placeholder-slate-500 dark:focus:bg-slate-700',
		className
	]
		.filter(Boolean)
		.join(' ');
}
