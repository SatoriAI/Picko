// @ts-nocheck
import type { PageLoad } from './$types';
import { error } from '@sveltejs/kit';

export interface ParticipantData {
	name: string;
	token: string;
	email?: string | null;
}

export interface EventData {
	id: string;
	name: string;
	maxAmount: number | null;
	date: string | null;
	currency: string | null;
	participants: ParticipantData[];
	drawComplete: boolean;
	assignments: Array<{ giver: string; receiver: string }> | null;
}

interface BackendParticipant {
	id: number;
	name: string;
	email: string | null;
	reveal_token: string | null;
}

interface BackendEvent {
	id: number;
	name: string;
	max_amount: number | null;
	date: string | null;
	currency: string | null;
	participants: BackendParticipant[];
}

export const load = async ({ params, fetch }: Parameters<PageLoad>[0]) => {
	const eventId = params.id;

	const response = await fetch(`/api/event/${eventId}`);
	if (response.status === 404) {
		throw error(404, 'Event not found');
	}
	if (!response.ok) {
		throw error(response.status, 'Failed to load event');
	}

	const backendEvent = (await response.json()) as BackendEvent;
	const hasAssignments = backendEvent.participants.some((p) => p.reveal_token);

	const event: EventData = {
		id: String(backendEvent.id),
		name: backendEvent.name,
		maxAmount: backendEvent.max_amount,
		date: backendEvent.date,
		currency: backendEvent.currency,
		participants: backendEvent.participants.map((p) => ({
			name: p.name,
			email: p.email,
			token: p.reveal_token ?? String(p.id)
		})),
		drawComplete: hasAssignments,
		assignments: null
	};

	return {
		event
	};
};
