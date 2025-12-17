/**
 * Shared types for Event data structures.
 * Used across multiple pages (event dashboard, registration, etc.)
 */

// ============================================
// Frontend Types (camelCase)
// ============================================

/**
 * Minimal participant info (used in public views like registration).
 */
export interface ParticipantSummary {
	id: number;
	name: string;
	wishlist: string | null;
}

/**
 * Full participant data (used in admin/dashboard views).
 */
export interface ParticipantData extends ParticipantSummary {
	email?: string | null;
	language: string;
	shareToken?: string | null;
}

/**
 * Base event data structure.
 */
interface EventBase {
	id: number | string;
	name: string;
	maxAmount: number | null;
	date: string | null;
	currency: string | null;
	registrationDeadline: string;
	registrationToken: string;
	isDrawComplete: boolean;
}

/**
 * Full event data with detailed participant info (for admin/dashboard views).
 */
export interface EventData extends EventBase {
	participants: ParticipantData[];
}

/**
 * Event data with summary participant info (for public views like registration).
 */
export interface RegistrationEventData extends EventBase {
	participants: ParticipantSummary[];
}

/**
 * Minimal event info used in status pages.
 */
export interface EventInfo {
	id: number;
	name: string;
	date: string | null;
	maxAmount: number | null;
	currency: string | null;
	registrationDeadline: string;
	isDrawComplete: boolean;
}

// ============================================
// Backend Types (snake_case) - for API responses
// ============================================

export interface BackendParticipant {
	id: number;
	name: string;
	email: string | null;
	language: string;
	wishlist: string | null;
	reveal_token: string | null;
}

export interface BackendEvent {
	id: number;
	name: string;
	max_amount: number | null;
	date: string | null;
	currency: string | null;
	registration_deadline: string;
	registration_token: string;
	is_draw_complete: boolean;
	participants: BackendParticipant[];
}

// ============================================
// Transformers
// ============================================

/**
 * Transforms a backend event response to frontend format.
 */
export function transformEvent(backend: BackendEvent): EventData {
	return {
		id: backend.id,
		name: backend.name,
		maxAmount: backend.max_amount,
		date: backend.date,
		currency: backend.currency,
		registrationDeadline: backend.registration_deadline,
		registrationToken: backend.registration_token,
		isDrawComplete: backend.is_draw_complete,
		participants: backend.participants.map(transformParticipant)
	};
}

/**
 * Transforms a backend participant to frontend format.
 */
export function transformParticipant(backend: BackendParticipant): ParticipantData {
	return {
		id: backend.id,
		name: backend.name,
		email: backend.email,
		language: backend.language,
		wishlist: backend.wishlist,
		shareToken: backend.reveal_token
	};
}

/**
 * Transforms a backend event to minimal EventInfo format.
 */
export function transformEventInfo(backend: BackendEvent): EventInfo {
	return {
		id: backend.id,
		name: backend.name,
		date: backend.date,
		maxAmount: backend.max_amount,
		currency: backend.currency,
		registrationDeadline: backend.registration_deadline,
		isDrawComplete: backend.is_draw_complete
	};
}
