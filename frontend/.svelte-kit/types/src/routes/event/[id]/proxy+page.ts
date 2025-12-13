// @ts-nocheck
import type { PageLoad } from './$types';

// Types that will match your backend API response
export interface ParticipantData {
	name: string;
	token: string;
}

export interface EventData {
	id: string;
	name: string;
	maxAmount: number;
	date: string | null;
	participants: ParticipantData[];
	drawComplete: boolean;
	assignments: Array<{ giver: string; receiver: string }> | null;
}

// Helper to generate mock tokens (remove when backend is ready)
function generateMockToken(): string {
	return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export const load = async ({ params }: Parameters<PageLoad>[0]) => {
	const eventId = params.id;

	// =================================================================
	// TODO: Replace this mock data with actual API call when backend is ready
	// Example:
	//
	// const response = await fetch(`/api/events/${eventId}`);
	// if (!response.ok) {
	//   throw error(404, 'Event not found');
	// }
	// const event: EventData = await response.json();
	// return { event };
	// =================================================================

	// Mock data for development
	const mockEvent: EventData = {
		id: eventId,
		name: 'Family Christmas 2025',
		maxAmount: 150,
		date: '2025-12-24',
		participants: [
			{ name: 'Mom', token: generateMockToken() },
			{ name: 'Dad', token: generateMockToken() },
			{ name: 'Anna', token: generateMockToken() },
			{ name: 'Ben', token: generateMockToken() },
			{ name: 'Grandma', token: generateMockToken() },
			{ name: 'Grandpa', token: generateMockToken() }
		],
		drawComplete: false,
		assignments: null
	};

	return {
		event: mockEvent
	};
};
