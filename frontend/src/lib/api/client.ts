export class ApiError extends Error {
	status: number;
	bodyText?: string;

	constructor(status: number, message: string, bodyText?: string) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
		this.bodyText = bodyText;
	}
}

async function safeReadText(response: Response): Promise<string | undefined> {
	try {
		return await response.text();
	} catch {
		return undefined;
	}
}

type FetchLike = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export async function fetchJson<T>(
	input: RequestInfo | URL,
	init?: (RequestInit & { fetch?: FetchLike }) | undefined
): Promise<T> {
	const fetchFn: FetchLike = init?.fetch ?? fetch;
	const { fetch: _fetch, ...requestInit } = init ?? {};

	const response = await fetchFn(input, requestInit);
	if (!response.ok) {
		throw new ApiError(response.status, `Request failed (${response.status})`, await safeReadText(response));
	}
	return (await response.json()) as T;
}
