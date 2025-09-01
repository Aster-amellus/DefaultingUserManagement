import Login from './pages/Login'
import Customers from './pages/Customers'
import Applications from './pages/Applications'
import Reasons from './pages/Reasons'
import Stats from './pages/Stats'
import Users from './pages/Users'
import Audit from './pages/Audit'
import type { Role } from './stores/auth'

export type AppRoute = {
  path: string
  element: React.ComponentType<any>
  roles?: Role[] // if omitted, accessible by all authenticated roles
  public?: boolean // true if accessible without auth (e.g. login)
}

export const allRoutes: AppRoute[] = [
  { path: '/login', element: Login, public: true },
  { path: '/customers', element: Customers, roles: ['Operator', 'Admin'] },
  { path: '/applications', element: Applications, roles: ['Operator', 'Reviewer', 'Admin'] },
  { path: '/reasons', element: Reasons, roles: ['Admin'] },
  { path: '/users', element: Users, roles: ['Admin'] },
  { path: '/stats', element: Stats, roles: ['Operator', 'Reviewer', 'Admin'] },
  { path: '/audit', element: Audit, roles: ['Admin'] },
]

export function routesForRole(role: Role | null): AppRoute[] {
  return allRoutes.filter((r) => {
    if (r.public) return true
    if (!role) return false
    return !r.roles || r.roles.includes(role)
  })
}
