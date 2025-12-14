import type { RequestHandler } from './$types';
import { proxyToBackend } from '$lib/server/proxy';

export const GET: RequestHandler = async (event) => {
	return proxyToBackend(event, { method: 'GET', path: `/draw/reveal/${event.params.token}` });
};
