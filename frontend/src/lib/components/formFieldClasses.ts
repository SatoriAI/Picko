/**
 * Shared styling classes for form input elements (Input, TextArea)
 */
export function getFormFieldClasses(darkMode: boolean, className: string = ''): string {
	const base =
		'w-full rounded-xl border-[1.5px] px-4 py-3 text-base transition-all focus:border-rose-500 focus:ring-[3px] focus:ring-rose-500/10 focus:outline-none';

	const theme = darkMode
		? 'border-slate-600 bg-slate-700/50 text-white placeholder-slate-500 focus:bg-slate-700'
		: 'border-slate-200 bg-slate-50 text-slate-800 placeholder-slate-400 focus:bg-white';

	return `${base} ${theme} ${className}`.trim();
}
