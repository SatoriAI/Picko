type SupportedLocale = 'pl' | 'en' | string;

function toIntlLocale(locale: SupportedLocale): string {
	if (locale === 'pl') return 'pl-PL';
	if (locale === 'en') return 'en-US';
	return locale;
}

type FormatDateOptions = {
	empty?: string;
};

export function formatDateLong(dateStr: string | null | undefined, locale: SupportedLocale, opts?: FormatDateOptions): string {
	if (!dateStr) return opts?.empty ?? '';
	const date = new Date(dateStr);
	if (!Number.isFinite(date.getTime())) return opts?.empty ?? '';

	return date.toLocaleDateString(toIntlLocale(locale), {
		year: 'numeric',
		month: 'long',
		day: 'numeric'
	});
}
