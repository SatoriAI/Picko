import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';

export interface EventData {
	id: number;
	name: string;
	maxAmount: number | null;
	date: string | null;
	currency: string | null;
	registrationDeadline: string;
	registrationToken: string;
	isDrawComplete: boolean;
	participants: Array<{
		id: number;
		name: string;
		wishlist: string | null;
	}>;
}

interface BackendEvent {
	id: number;
	name: string;
	max_amount: number | null;
	date: string | null;
	currency: string | null;
	registration_deadline: string;
	registration_token: string;
	is_draw_complete: boolean;
	participants: Array<{
		id: number;
		name: string;
		email: string | null;
		language: string;
		wishlist: string | null;
	}>;
}

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await fetch(`/api/event/register/${params.token}`);

	if (response.status === 404) {
		throw error(404, 'Event not found');
	}
	if (!response.ok) {
		throw error(response.status, 'Failed to load event');
	}

	const backendEvent = (await response.json()) as BackendEvent;

	const event: EventData = {
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
