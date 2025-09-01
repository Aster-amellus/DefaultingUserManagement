import { Layout, Menu, Button } from 'antd'
import { useEffect, useMemo } from 'react'
import { Routes, Route, useNavigate, Link, Navigate } from 'react-router-dom'
import { allRoutes, routesForRole, type AppRoute } from './routes'
import { useAuthStore } from './stores/auth'
import { http } from './lib/http'

const { Header, Sider, Content } = Layout

export default function App() {
  const navigate = useNavigate()
  const { token, role, clear } = useAuthStore()
  const isAuthed = !!token
  const visibleRoutes: AppRoute[] = useMemo(() => routesForRole(role), [role])

  useEffect(() => {
    if (!isAuthed) navigate('/login')
  }, [isAuthed])

  useEffect(() => {
    // on load, if token exists but role is null, fetch /users/me
    async function syncRole() {
      if (!token || role) return
      try {
        const me = await http.get('/users/me')
        const r = (me.data.role as string)
        if (r?.toLowerCase() === 'admin') useAuthStore.getState().setAuth(token, 'Admin')
        else if (r?.toLowerCase() === 'reviewer') useAuthStore.getState().setAuth(token, 'Reviewer')
        else useAuthStore.getState().setAuth(token, 'Operator')
      } catch {}
    }
    syncRole()
  }, [token, role])

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible>
        <div style={{ color: '#fff', padding: 16, fontWeight: 600 }}>违约客户管理</div>
        <Menu
          theme="dark"
          mode="inline"
          items={visibleRoutes
            .filter((r: AppRoute) => !r.public)
            .map((r: AppRoute) => ({ key: r.path, label: <Link to={r.path}>{labelOf(r.path)}</Link> }))}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          {isAuthed && <Button onClick={clear}>退出登录</Button>}
        </Header>
        <Content style={{ margin: 16 }}>
          <Routes>
            {allRoutes.map((r: AppRoute) => (
              <Route
                key={r.path}
                path={r.path}
                element={r.public ? <r.element /> : (isAuthed && (!r.roles || (role && r.roles.includes(role))) ? <r.element /> : <Navigate to="/login" replace />)}
              />
            ))}
            <Route path="/" element={<Navigate to={isAuthed ? (visibleRoutes.find(r=>!r.public)?.path || '/customers') : '/login'} replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

function labelOf(path: string) {
  switch (path) {
    case '/customers': return '客户'
    case '/applications': return '申请'
    case '/reasons': return '原因'
    case '/stats': return '统计'
    case '/audit': return '审计'
    default: return path
  }
}
