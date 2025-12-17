/**
 * Shared type definitions for the application.
 */

// Event types
export type {
	ParticipantSummary,
	ParticipantData,
	EventData,
	RegistrationEventData,
	EventInfo,
	BackendParticipant,
	BackendEvent
} from './event';

export { transformEvent, transformParticipant, transformEventInfo } from './event';

// Assignment types
export type { AssignmentData, AssignmentInfo, MyStatusData } from './assignment';
