<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { fetchJson } from '$lib/api/client';
	import { createFeedbackState } from '$lib/utils/feedback.svelte';
	import { CheckIcon, CopyIcon, MailIcon, IconButton } from '$lib/components';

	interface Participant {
		id: number;
		name: string;
		shareToken: string | null;
		email?: string | null;
		language?: string;
		wishlist?: string | null;
	}

	interface Props {
		participant: Participant;
		onUpdate?: (updated: Participant) => void;
	}

	let { participant, onUpdate }: Props = $props();

	// Local state
	let isExpanded = $state(false);
	let emailDraft = $state(participant.email ?? '');
	let isSaving = $state(false);

	// Feedback states using the utility
	const saved = createFeedbackState(1500);
	const copied = createFeedbackState(2000);

	function toggleExpand() {
		isExpanded = !isExpanded;
		if (isExpanded) {
			emailDraft = participant.email ?? '';
		}
	}

	async function handleSaveEmail() {
		isSaving = true;
		saved.reset();
		try {
			const email = emailDraft.trim();
			const payload = { email: email.length ? email : null };

			const updated = await fetchJson<{ id: number; email: string | null; name: string }>(
				`/api/participant/${participant.id}`,
				{
					method: 'PATCH',
					body: JSON.stringify(payload)
				}
			);

			onUpdate?.({ ...participant, email: updated.email });

			saved.trigger();
			isExpanded = false;
		} catch (err) {
			console.error('Failed to update participant email', err);
			alert(m.validation_error());
		} finally {
			isSaving = false;
		}
	}

	async function copyLink() {
		if (!participant.shareToken) return;
		const link = `${window.location.origin}/join/${participant.shareToken}`;
		try {
			await navigator.clipboard.writeText(link);
			copied.trigger();
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}
</script>

<div
	class="rounded-xl border border-slate-200 bg-white transition-colors dark:border-slate-700 dark:bg-slate-800/50"
>
	<!-- Main row: Avatar, Name, Actions -->
	<div class="flex items-center gap-3 p-3">
		<!-- Avatar -->
		<div
			class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-slate-100 to-slate-200 text-sm font-semibold text-slate-600 dark:from-slate-600 dark:to-slate-700 dark:text-slate-200"
		>
			{participant.name.charAt(0).toUpperCase()}
		</div>

		<!-- Name and email info -->
		<div class="min-w-0 flex-1">
			<div class="font-medium text-slate-800 dark:text-white">
				{participant.name}
			</div>
			{#if participant.email}
				<div class="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
					<MailIcon class="h-3 w-3" />
					<span class="truncate">{participant.email}</span>
				</div>
			{/if}
		</div>

		<!-- Actions -->
		<div class="flex shrink-0 items-center gap-2">
			<!-- Add/Edit Email Button -->
			<button
				type="button"
				onclick={toggleExpand}
				class="flex cursor-pointer items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all {isExpanded
					? 'bg-orange-50 text-orange-600 dark:bg-slate-700 dark:text-orange-400'
					: 'text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200'}"
			>
				<MailIcon class="h-3.5 w-3.5" />
				<span class="hidden sm:inline"
					>{participant.email ? m.admin_edit_email() : m.admin_add_email()}</span
				>
			</button>

			<!-- Copy Link Button -->
			<IconButton variant={copied.active ? 'success' : 'default'} onclick={copyLink}>
				{#if copied.active}
					<CheckIcon class="h-4 w-4" />
					<span class="hidden sm:inline">{m.admin_copied()}</span>
				{:else}
					<CopyIcon class="h-4 w-4" />
					<span class="hidden sm:inline">{m.admin_copy_link()}</span>
				{/if}
			</IconButton>
		</div>
	</div>

	<!-- Expandable email edit section -->
	{#if isExpanded}
		<div class="border-t border-slate-100 px-3 py-3 dark:border-slate-700/50">
			<div class="flex flex-col gap-2 sm:flex-row sm:items-center">
				<div class="relative flex-1">
					<MailIcon
						class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-slate-500"
					/>
					<input
						type="email"
						bind:value={emailDraft}
						placeholder={m.admin_email_placeholder()}
						class="w-full cursor-text rounded-lg border border-slate-200 bg-slate-50 py-2 pl-10 pr-3 text-sm text-slate-800 transition-colors placeholder-slate-400 focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 dark:border-slate-600 dark:bg-slate-700/50 dark:text-white dark:placeholder-slate-500"
					/>
				</div>
				<IconButton
					variant={saved.active ? 'success' : 'primary'}
					onclick={handleSaveEmail}
					disabled={isSaving}
				>
					{#if saved.active}
						<CheckIcon class="h-4 w-4" />
						<span>{m.admin_email_saved()}</span>
					{:else if isSaving}
						<span>{m.admin_email_saving()}</span>
					{:else}
						<span>{m.admin_save_email()}</span>
					{/if}
				</IconButton>
			</div>
		</div>
	{/if}
</div>
