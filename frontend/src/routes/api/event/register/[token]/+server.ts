import type { RequestHandler } from './$types';
import { proxyToBackend } from '$lib/server/proxy';

export const GET: RequestHandler = async (event) => {
	return proxyToBackend(event, { method: 'GET', path: `/event/register/${event.params.token}` });
};

export const POST: RequestHandler = async (event) => {
	return proxyToBackend(event, { method: 'POST', path: `/event/register/${event.params.token}` });
};
