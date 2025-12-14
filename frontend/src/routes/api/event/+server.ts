import type { RequestHandler } from './$types';
import { proxyToBackend } from '$lib/server/proxy';

export const POST: RequestHandler = async (event) => {
	return proxyToBackend(event, { method: 'POST', path: '/event' });
};
