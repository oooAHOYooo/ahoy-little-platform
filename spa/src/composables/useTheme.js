import { ref } from 'vue'

const THEME_KEY = 'ahoyTheme'
const currentTheme = ref('deep-blue')

export function useTheme() {
    function initTheme() {
        const saved = localStorage.getItem(THEME_KEY)
        if (saved) {
            setTheme(saved)
        } else {
            setTheme('deep-blue')
        }
    }

    function setTheme(theme) {
        currentTheme.value = theme
        localStorage.setItem(THEME_KEY, theme)

        // Remove existing theme classes
        document.body.classList.remove('theme-after-dark', 'theme-deep-blue')

        // Add new theme class if not default
        if (theme === 'after-dark') {
            document.body.classList.add('theme-after-dark')
        } else if (theme === 'deep-blue') {
            document.body.classList.add('theme-deep-blue')
        }
    }

    return {
        currentTheme,
        initTheme,
        setTheme
    }
}
