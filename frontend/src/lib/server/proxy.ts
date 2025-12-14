import { env } from '$env/dynamic/private';

const DEFAULT_API_BASE_URL = 'http://localhost:8010';

function joinUrl(base: string, path: string): string {
	const normalizedBase = base.endsWith('/') ? base : `${base}/`;
	const normalizedPath = path.startsWith('/') ? path.slice(1) : path;
	return new URL(normalizedPath, normalizedBase).toString();
}

function getApiBaseUrl(): string {
	return env.API_BASE_URL ?? DEFAULT_API_BASE_URL;
}

type ProxyEvent = {
	request: Request;
	fetch: typeof fetch;
};

type ProxyToBackendOptions = {
	method: string;
	path: string;
	/**
	 * If omitted, forwards the incoming request body for non-GET/HEAD requests.
	 * Set to false to explicitly avoid reading/forwarding the body.
	 */
	forwardBody?: boolean;
};

export async function proxyToBackend(event: ProxyEvent, opts: ProxyToBackendOptions): Promise<Response> {
	const url = joinUrl(getApiBaseUrl(), opts.path);
	const method = opts.method.toUpperCase();
	const forwardBody = opts.forwardBody ?? (method !== 'GET' && method !== 'HEAD');

	let body: string | undefined;
	const headers: Record<string, string> = {};

	if (forwardBody) {
		body = await event.request.text();
		headers['content-type'] = event.request.headers.get('content-type') ?? 'application/json';
	}

	const upstream = await event.fetch(url, {
		method,
		headers,
		body
	});

	return new Response(await upstream.text(), {
		status: upstream.status,
		headers: {
			'content-type': upstream.headers.get('content-type') ?? 'application/json'
		}
	});
}
