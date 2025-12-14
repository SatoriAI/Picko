import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const API_BASE_URL = env.API_BASE_URL ?? 'http://localhost:8010';

export const GET: RequestHandler = async ({ params, fetch }) => {
	const token = params.token;
	const upstream = await fetch(`${API_BASE_URL}/draw/reveal/${token}`, {
		method: 'GET'
	});

	return new Response(await upstream.text(), {
		status: upstream.status,
		headers: {
			'content-type': upstream.headers.get('content-type') ?? 'application/json'
		}
	});
};
