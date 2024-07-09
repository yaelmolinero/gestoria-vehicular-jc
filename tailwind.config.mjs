/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			screens: {
				'sm': '576px',
				'md': '768px',
				'lg': '992px',
				'xl': '1200px',
				'xxl': '1400px'
			}
		},
	},
	plugins: [],
}
