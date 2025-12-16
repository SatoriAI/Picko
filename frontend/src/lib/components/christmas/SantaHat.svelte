<!-- Santa hat to overlay on the gift emoji -->
<svg
	class="santa-hat"
	viewBox="0 0 32 32"
	fill="none"
	xmlns="http://www.w3.org/2000/svg"
	aria-hidden="true"
>
	<!-- Hat body -->
	<path
		d="M6 20C6 20 8 8 18 6C28 4 30 14 30 14L28 20H6Z"
		fill="#dc2626"
		stroke="#b91c1c"
		stroke-width="0.5"
	/>
	<!-- White fur trim -->
	<ellipse cx="17" cy="21" rx="13" ry="3" fill="#fef2f2" stroke="#e5e5e5" stroke-width="0.3" />
	<!-- Pompom -->
	<circle cx="30" cy="12" r="4" fill="#fef2f2" stroke="#e5e5e5" stroke-width="0.3" />
	<!-- Highlight on hat -->
	<path d="M10 14C10 14 12 10 18 9" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" />
</svg>

<style>
	.santa-hat {
		position: absolute;
		width: 20px;
		height: 20px;
		top: -8px;
		left: 8px;
		transform: rotate(-15deg);
		filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.15));
		z-index: 10;
	}
</style>
