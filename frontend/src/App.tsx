import { Layout, Menu, theme } from 'antd'
import { useEffect } from 'react'
import { Routes, Route, useNavigate, Link } from 'react-router-dom'
import { routes } from './routes'
import { useAuthStore } from './stores/auth'

const { Header, Sider, Content } = Layout

export default function App() {
  const navigate = useNavigate()
  const isAuthed = useAuthStore(s => !!s.token)

  useEffect(() => {
    if (!isAuthed) navigate('/login')
  }, [isAuthed])

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible>
        <div style={{ color: '#fff', padding: 16, fontWeight: 600 }}>违约客户管理</div>
        <Menu theme="dark" mode="inline">
          <Menu.Item key="customers"><Link to="/customers">客户</Link></Menu.Item>
          <Menu.Item key="applications"><Link to="/applications">申请</Link></Menu.Item>
          <Menu.Item key="reasons"><Link to="/reasons">原因</Link></Menu.Item>
          <Menu.Item key="stats"><Link to="/stats">统计</Link></Menu.Item>
          <Menu.Item key="audit"><Link to="/audit">审计</Link></Menu.Item>
        </Menu>
      </Sider>
      <Layout>
        <Header style={{ background: '#fff' }} />
        <Content style={{ margin: 16 }}>
          <Routes>
            {routes.map(r => <Route key={r.path} path={r.path} element={<r.element/>} />)}
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}
