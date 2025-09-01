import '@testing-library/jest-dom'

// Polyfill matchMedia for Ant Design in jsdom
if (typeof window !== 'undefined' && !(window as any).matchMedia) {
	;(window as any).matchMedia = (query: string) => ({
		matches: false,
		media: query,
		onchange: null,
		addEventListener: () => {},
		removeEventListener: () => {},
		addListener: () => {},
		removeListener: () => {},
		dispatchEvent: () => false,
	})
}