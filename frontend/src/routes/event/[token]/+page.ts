import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { EventData, BackendEvent } from '$lib/types';
import { transformEvent } from '$lib/types';

export type { EventData };

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await fetch(`/api/event/${params.token}`);
	if (response.status === 404) {
		throw error(404, 'Event not found');
	}
	if (!response.ok) {
		throw error(response.status, 'Failed to load event');
	}

	const backendEvent = (await response.json()) as BackendEvent;
	const event = transformEvent(backendEvent);

	return {
		event
	};
};
