import type { Locale } from '$lib/paraglide/runtime';
import type { GuideId } from './paths';
import { en } from './en';
import { pl } from './pl';

export { GUIDE_IDS, guideRoute, isGuideId, type GuideId } from './paths';

export interface GuideSection {
	heading: string;
	paragraphs: string[];
	list?: string[];
}

/**
 * One guide in one language. Long-form text lives here rather than in messages/*.json: it is page content, not
 * interface strings, and each language is written for its own searches rather than translated line by line.
 *
 * Every claim about Picko must match what the app does (see the homepage FAQ); change both when the rules change.
 */
export interface Guide {
	/** The <title>: about 60 characters, the main search phrase first. */
	seoTitle: string;
	/** The meta description: about 150 characters. */
	description: string;
	/** The H1. */
	title: string;
	/** One line for the guide's card on the homepage and under other guides. */
	summary: string;
	intro: string[];
	sections: GuideSection[];
}

/** When the guides first went live, for the Article structured data. */
export const GUIDES_PUBLISHED = '2026-11-18';

export const GUIDES: Record<Locale, Record<GuideId, Guide>> = { en, pl };
