import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			pages: '../web',
			assets: '../web',
			fallback: 'index.html',
			precompress: false,
			strict: false
		}),
		paths: {
			base: process.env.BASE_PATH || ''
		}
	}
};

export default config;
