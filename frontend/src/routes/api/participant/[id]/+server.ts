import type { RequestHandler } from './$types';
import { proxyToBackend } from '$lib/server/proxy';

export const PATCH: RequestHandler = async (event) => {
	return proxyToBackend(event, { method: 'PATCH', path: `/participant/${event.params.id}` });
};
