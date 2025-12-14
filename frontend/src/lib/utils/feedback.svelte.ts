/**
 * Creates a reactive feedback state that auto-resets after a duration.
 * Useful for showing temporary success/copied/saved indicators.
 *
 * @example
 * const copied = createFeedbackState(2000);
 * // In handler: copied.trigger();
 * // In template: {#if copied.active}...{/if}
 */
export function createFeedbackState(durationMs = 2000) {
	let active = $state(false);
	let timeoutId: ReturnType<typeof setTimeout> | null = null;

	function trigger() {
		// Clear any existing timeout to prevent race conditions
		if (timeoutId) {
			clearTimeout(timeoutId);
		}

		active = true;
		timeoutId = setTimeout(() => {
			active = false;
			timeoutId = null;
		}, durationMs);
	}

	function reset() {
		if (timeoutId) {
			clearTimeout(timeoutId);
			timeoutId = null;
		}
		active = false;
	}

	return {
		get active() {
			return active;
		},
		trigger,
		reset
	};
}
