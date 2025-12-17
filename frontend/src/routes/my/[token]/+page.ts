import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';
import type { MyStatusData } from '$lib/types';

export type { MyStatusData };

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
