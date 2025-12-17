<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { PageLayout, GiftBoxReveal } from '$lib/components';
	import type { AssignmentData } from '$lib/types';

	// Props from loader
	let { data } = $props();
	const assignment: AssignmentData = data.assignment;
</script>

<svelte:head>
	<title>{m.join_page_title()}</title>
</svelte:head>

<PageLayout isHeaderLink>
	<div class="flex min-h-[70vh] flex-col items-center justify-center py-8">
		<GiftBoxReveal
			giverName={assignment.giver_name}
			receiverName={assignment.receiver_name}
			receiverWishlist={assignment.receiver_wishlist}
			eventName={assignment.event.name}
			eventDate={assignment.event.date}
			maxAmount={assignment.event.max_amount}
			currency={assignment.event.currency}
		/>
	</div>
</PageLayout>
