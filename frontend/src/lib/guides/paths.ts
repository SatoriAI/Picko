// The guides' public addresses. vite.config.ts reads this file to build Paraglide's URL patterns, so it must not
// import anything that only exists once the app is built ($lib aliases, generated Paraglide files).

/** Each guide's address per language. The slugs are what people search for, so they are written per language. */
export const GUIDE_PATHS = {
	organize: { en: '/en/how-to-organize-secret-santa', pl: '/pl/jak-zorganizowac-mikolajki' },
	work: { en: '/en/secret-santa-at-work', pl: '/pl/mikolajki-w-pracy' },
	family: { en: '/en/family-secret-santa', pl: '/pl/losowanie-prezentow-w-rodzinie' },
	remote: { en: '/en/virtual-secret-santa', pl: '/pl/mikolajki-na-odleglosc' }
} as const;

export type GuideId = keyof typeof GUIDE_PATHS;

export const GUIDE_IDS = Object.keys(GUIDE_PATHS) as GuideId[];

/** The route a guide is served from inside the app; Paraglide maps it to and from the public addresses. */
export const guideRoute = (id: GuideId) => `/guides/${id}` as const;

export const isGuideId = (value: string): value is GuideId => Object.hasOwn(GUIDE_PATHS, value);
