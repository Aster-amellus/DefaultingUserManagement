import { Button, Card, Form, Input, message } from 'antd'
import { http } from '../lib/http'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/auth'

export default function Login() {
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)

  const onFinish = async (values: any) => {
    try {
      const form = new URLSearchParams()
      form.set('username', values.email)
      form.set('password', values.password)
  const { data } = await http.post('/auth/token', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
      // 暂无角色查询接口，这里假设登录即为未知角色；后续可通过 /users/me 获得
      setAuth(data.access_token, 'Operator')
      navigate('/customers')
    } catch (e: any) {
      message.error('登录失败')
    }
  }

  return (
    <div style={{ display: 'grid', placeItems: 'center', height: '100vh' }}>
      <Card title="登录" style={{ width: 360 }}>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item label="邮箱" name="email" rules={[{ required: true, message: '请输入邮箱' }]}> 
            <Input />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true, message: '请输入密码' }]}> 
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>登录</Button>
        </Form>
      </Card>
    </div>
  )
}
