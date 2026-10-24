import { createContext, useContext, type ReactNode } from 'react'

import type { Bootstrap } from '../lib/api'
import { useApi, usePoll } from '../lib/hooks'

interface AppCtx {
  data: Bootstrap | null
  loading: boolean
  error: string | null
  reload: (quiet?: boolean) => Promise<void>
}

const Ctx = createContext<AppCtx>({ data: null, loading: true, error: null, reload: async () => {} })

export function AppProvider({ children }: { children: ReactNode }) {
  const { data, loading, error, reload } = useApi<Bootstrap>('/api/bootstrap')
  usePoll(() => reload(true), 60_000, !!data)

  return <Ctx.Provider value={{ data, loading, error, reload }}>{children}</Ctx.Provider>
}

export const useApp = () => useContext(Ctx)
