import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const API_BASE_URL = env.API_BASE_URL ?? 'http://localhost:8010';

export const POST: RequestHandler = async ({ request, fetch }) => {
	const body = await request.text();

	let contentType = request.headers.get('content-type');
	if (!contentType) contentType = 'application/json';

	const upstream = await fetch(`${API_BASE_URL}/event`, {
		method: 'POST',
		headers: {
			'content-type': contentType
		},
		body
	});

	return new Response(await upstream.text(), {
		status: upstream.status,
		headers: {
			'content-type': upstream.headers.get('content-type') ?? 'application/json'
		}
	});
};
