import type { RequestHandler } from './$types';
import { proxyToBackend } from '$lib/server/proxy';

export const GET: RequestHandler = async (event) => {
	return proxyToBackend(event, { method: 'GET', path: `/participant/me/${event.params.token}` });
};
