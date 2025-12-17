/**
 * Shared types for Assignment/Draw data structures.
 * Used in reveal pages (join, my status).
 */

/**
 * Assignment data returned from the reveal endpoint.
 * Used in the join/[token] page.
 */
export interface AssignmentData {
	giver_name: string;
	receiver_name: string;
	receiver_wishlist: string | null;
	event: {
		name: string;
		date: string | null;
		max_amount: number | null;
		currency: string | null;
	};
}

/**
 * Minimal assignment info for the my status page.
 */
export interface AssignmentInfo {
	receiver_name: string;
	receiver_wishlist: string | null;
}

/**
 * Complete status data for the participant's personal page.
 */
export interface MyStatusData {
	participant_name: string;
	event: {
		id: number;
		name: string;
		date: string | null;
		max_amount: number | null;
		currency: string | null;
		registration_deadline: string;
		is_draw_complete: boolean;
	};
	assignment: AssignmentInfo | null;
}
