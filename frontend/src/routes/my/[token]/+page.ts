import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';

export interface EventInfo {
	id: number;
	name: string;
	date: string | null;
	max_amount: number | null;
	currency: string | null;
	registration_deadline: string;
	is_draw_complete: boolean;
}

export interface AssignmentInfo {
	receiver_name: string;
	receiver_wishlist: string | null;
}

export interface MyStatusData {
	participant_name: string;
	event: EventInfo;
	assignment: AssignmentInfo | null;
}

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await fetch(`/api/participant/me/${params.token}`);

	if (response.status === 404) {
		throw error(404, 'Your link is invalid or has expired.');
	}
	if (!response.ok) {
		throw error(response.status, 'Failed to load your status');
	}

	const data: MyStatusData = await response.json();

	return {
		...data,
		token: params.token
	};
};
