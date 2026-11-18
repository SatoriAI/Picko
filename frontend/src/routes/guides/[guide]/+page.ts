import { error } from '@sveltejs/kit';
import { isGuideId } from '$lib/guides';
import type { PageLoad } from './$types';

// Reached through each guide's localized address (e.g. /pl/mikolajki-w-pracy), which the reroute hook maps here.
export const load: PageLoad = ({ params }) => {
	if (!isGuideId(params.guide)) error(404);
	return { id: params.guide };
};
