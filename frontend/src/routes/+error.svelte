<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { PageLayout, Card, ActionLink } from '$lib/components';

	const notFound = $derived(page.status === 404);
	const title = $derived(notFound ? m.error_not_found_title() : m.error_generic_title());
</script>

<svelte:head>
	<title>{title} | {m.app_name()}</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<PageLayout>
	<section class="py-12 sm:py-16">
		<Card class="mx-auto max-w-md text-center">
			<p class="mb-2 text-5xl font-bold text-rose-500">{page.status}</p>
			<h1 class="mb-3 text-2xl font-bold tracking-tight text-slate-800 dark:text-white">
				{title}
			</h1>
			<p class="mb-6 text-slate-500 dark:text-slate-400">
				{notFound ? m.error_not_found_desc() : m.error_generic_desc()}
			</p>
			<ActionLink href={resolve('/')} external={false}>{m.admin_back_home()}</ActionLink>
		</Card>
	</section>
</PageLayout>
