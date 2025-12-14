import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';

export interface AssignmentData {
	giver_name: string;
	receiver_name: string;
	receiver_wishlist: string | null;
	event: {
		name: string;
		date: string | null;
		max_amount: number | null;
		currency: string | null;
	};
}

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await fetch(`/api/draw/reveal/${params.token}`);

	if (!response.ok) {
		if (response.status === 404) {
			throw error(404, {
				message: "Assignment not found. The link may be invalid or the draw hasn't happened yet."
			});
		}
		throw error(response.status, { message: 'Failed to load assignment' });
	}

	const assignment: AssignmentData = await response.json();

	return {
		assignment,
		token: params.token
	};
};
