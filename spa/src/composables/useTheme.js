import { ref } from 'vue'

const THEME_KEY = 'ahoyTheme'
const currentTheme = ref('default')

export function useTheme() {
    function initTheme() {
        const saved = localStorage.getItem(THEME_KEY)
        if (saved) {
            setTheme(saved)
        } else {
            setTheme('default')
        }
    }

    function setTheme(theme) {
        currentTheme.value = theme
        localStorage.setItem(THEME_KEY, theme)

        // Remove existing theme classes
        document.body.classList.remove('theme-after-dark')

        // Add new theme class if not default
        if (theme === 'after-dark') {
            document.body.classList.add('theme-after-dark')
        }
    }

    return {
        currentTheme,
        initTheme,
        setTheme
    }
}
