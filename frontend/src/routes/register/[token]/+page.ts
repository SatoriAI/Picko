import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { RegistrationEventData, BackendEvent } from '$lib/types';

export type { RegistrationEventData as EventData };

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await fetch(`/api/event/register/${params.token}`);

	if (response.status === 404) {
		throw error(404, 'Event not found');
	}
	if (!response.ok) {
		throw error(response.status, 'Failed to load event');
	}

	const backendEvent = (await response.json()) as BackendEvent;

	// Transform to frontend format (registration page only needs summary participant info)
	const event: RegistrationEventData = {
		id: backendEvent.id,
		name: backendEvent.name,
		maxAmount: backendEvent.max_amount,
		date: backendEvent.date,
		currency: backendEvent.currency,
		registrationDeadline: backendEvent.registration_deadline,
		registrationToken: backendEvent.registration_token,
		isDrawComplete: backendEvent.is_draw_complete,
		participants: backendEvent.participants.map((p) => ({
			id: p.id,
			name: p.name,
			wishlist: p.wishlist
		}))
	};

	return {
		event,
		token: params.token
	};
};
