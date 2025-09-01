import Login from './pages/Login'
import Customers from './pages/Customers'
import Applications from './pages/Applications'
import Reasons from './pages/Reasons'
import Stats from './pages/Stats'
import Audit from './pages/Audit'

export const routes = [
  { path: '/login', element: Login },
  { path: '/customers', element: Customers },
  { path: '/applications', element: Applications },
  { path: '/reasons', element: Reasons },
  { path: '/stats', element: Stats },
  { path: '/audit', element: Audit },
]
