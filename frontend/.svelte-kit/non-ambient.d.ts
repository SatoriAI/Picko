
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/api" | "/api/draw" | "/api/draw/reveal" | "/api/draw/reveal/[token]" | "/api/event" | "/api/event/register" | "/api/event/register/[token]" | "/api/event/[id]" | "/api/event/[id]/send-emails" | "/api/participant" | "/api/participant/me" | "/api/participant/me/[token]" | "/api/participant/[id]" | "/event" | "/event/[id]" | "/join" | "/join/[token]" | "/my" | "/my/[token]" | "/register" | "/register/[token]";
		RouteParams(): {
			"/api/draw/reveal/[token]": { token: string };
			"/api/event/register/[token]": { token: string };
			"/api/event/[id]": { id: string };
			"/api/event/[id]/send-emails": { id: string };
			"/api/participant/me/[token]": { token: string };
			"/api/participant/[id]": { id: string };
			"/event/[id]": { id: string };
			"/join/[token]": { token: string };
			"/my/[token]": { token: string };
			"/register/[token]": { token: string }
		};
		LayoutParams(): {
			"/": { token?: string; id?: string };
			"/api": { token?: string; id?: string };
			"/api/draw": { token?: string };
			"/api/draw/reveal": { token?: string };
			"/api/draw/reveal/[token]": { token: string };
			"/api/event": { token?: string; id?: string };
			"/api/event/register": { token?: string };
			"/api/event/register/[token]": { token: string };
			"/api/event/[id]": { id: string };
			"/api/event/[id]/send-emails": { id: string };
			"/api/participant": { token?: string; id?: string };
			"/api/participant/me": { token?: string };
			"/api/participant/me/[token]": { token: string };
			"/api/participant/[id]": { id: string };
			"/event": { id?: string };
			"/event/[id]": { id: string };
			"/join": { token?: string };
			"/join/[token]": { token: string };
			"/my": { token?: string };
			"/my/[token]": { token: string };
			"/register": { token?: string };
			"/register/[token]": { token: string }
		};
		Pathname(): "/" | "/api" | "/api/" | "/api/draw" | "/api/draw/" | "/api/draw/reveal" | "/api/draw/reveal/" | `/api/draw/reveal/${string}` & {} | `/api/draw/reveal/${string}/` & {} | "/api/event" | "/api/event/" | "/api/event/register" | "/api/event/register/" | `/api/event/register/${string}` & {} | `/api/event/register/${string}/` & {} | `/api/event/${string}` & {} | `/api/event/${string}/` & {} | `/api/event/${string}/send-emails` & {} | `/api/event/${string}/send-emails/` & {} | "/api/participant" | "/api/participant/" | "/api/participant/me" | "/api/participant/me/" | `/api/participant/me/${string}` & {} | `/api/participant/me/${string}/` & {} | `/api/participant/${string}` & {} | `/api/participant/${string}/` & {} | "/event" | "/event/" | `/event/${string}` & {} | `/event/${string}/` & {} | "/join" | "/join/" | `/join/${string}` & {} | `/join/${string}/` & {} | "/my" | "/my/" | `/my/${string}` & {} | `/my/${string}/` & {} | "/register" | "/register/" | `/register/${string}` & {} | `/register/${string}/` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/robots.txt" | string & {};
	}
}