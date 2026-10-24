import { createContext, useContext, useEffect, type ReactNode } from 'react'

import { useLocalStorage } from './lib/hooks'

type Theme = 'light' | 'dark'

const ThemeCtx = createContext<{ theme: Theme; toggle: () => void; set: (t: Theme) => void }>({
  theme: 'light',
  toggle: () => {},
  set: () => {},
})

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useLocalStorage<Theme>('devi-theme', 'light')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  return (
    <ThemeCtx.Provider value={{ theme, set: setTheme, toggle: () => setTheme(theme === 'light' ? 'dark' : 'light') }}>
      {children}
    </ThemeCtx.Provider>
  )
}

export const useTheme = () => useContext(ThemeCtx)
