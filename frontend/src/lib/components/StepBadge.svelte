<script lang="ts">
	interface Props {
		step: number;
		color: 'emerald' | 'amber' | 'rose';
		size?: 'sm' | 'md';
	}

	let { step, color, size = 'md' }: Props = $props();

	const colorClasses = {
		emerald: 'from-emerald-400 to-emerald-500 shadow-emerald-400/35',
		amber: 'from-amber-400 to-orange-500 shadow-orange-400/35',
		rose: 'from-rose-400 to-rose-500 shadow-rose-400/35'
	};

	const sizeClasses = {
		sm: 'h-6 w-6 text-xs',
		md: 'h-8 w-8 text-sm'
	};
</script>

<span
	class="flex items-center justify-center rounded-full bg-gradient-to-br font-bold text-white shadow-md {colorClasses[
		color
	]} {sizeClasses[size]}"
>
	{step}
</span>
