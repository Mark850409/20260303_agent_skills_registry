/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
    theme: {
        extend: {
            colors: {
                brand: {
                    50: '#eefbf3',
                    100: '#d6f5e3',
                    200: '#b0eac9',
                    300: '#7dd9a8',
                    400: '#48c082',
                    500: '#25a465',
                    600: '#178451',
                    700: '#136942',
                    800: '#125436',
                    900: '#10452e',
                }
            },
            fontFamily: {
                sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
                mono: ['"JetBrains Mono"', 'monospace'],
                display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
            }
        }
    },
    plugins: []
}
