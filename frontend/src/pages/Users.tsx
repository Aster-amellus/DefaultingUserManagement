import { Button, Card, Form, Input, Modal, Select, Space, Table, Tag, message } from 'antd'
import { useEffect, useState } from 'react'
import { http } from '../lib/http'

type Role = 'Admin' | 'Reviewer' | 'Operator'
type UserRow = {
  id: number
  email: string
  full_name?: string
  role: Role
  is_active: boolean
}

export default function Users() {
  const [data, setData] = useState<UserRow[]>([])
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()
  const [editForm] = Form.useForm()
  const [editing, setEditing] = useState<UserRow | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await http.get('/users/')
      setData(res.data)
    } catch { message.error('加载用户失败') } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const onCreate = async (v: any) => {
    try {
      await http.post('/users/', v)
      message.success('已创建/更新')
      form.resetFields()
      load()
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '创建失败')
    }
  }

  const onEdit = (row: UserRow) => {
    setEditing(row)
    editForm.setFieldsValue({ full_name: row.full_name, role: row.role, password: '' })
  }

  const onSave = async () => {
    const v = await editForm.validateFields()
    try {
      await http.patch(`/users/${editing!.id}`, v)
      message.success('已保存')
      setEditing(null)
      load()
    } catch (e: any) { message.error(e?.response?.data?.detail || '保存失败') }
  }

  const onDelete = async (row: UserRow) => {
    try {
      await http.delete(`/users/${row.id}`)
      message.success('已删除')
      load()
    } catch { message.error('删除失败') }
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Card title="创建用户">
        <Form layout="inline" form={form} onFinish={onCreate}>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, type: 'email' }]}><Input style={{ width: 220 }} /></Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}><Input.Password style={{ width: 180 }} /></Form.Item>
          <Form.Item name="full_name" label="姓名"><Input style={{ width: 160 }} /></Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true }]}>
            <Select style={{ width: 160 }} options={[{value:'Operator',label:'Operator'},{value:'Reviewer',label:'Reviewer'},{value:'Admin',label:'Admin'}]} />
          </Form.Item>
          <Button type="primary" htmlType="submit">创建</Button>
        </Form>
      </Card>

      <Card title="用户列表">
        <Table rowKey="id" loading={loading} dataSource={data} columns={[
          { title: 'ID', dataIndex: 'id', width: 80 },
          { title: '邮箱', dataIndex: 'email' },
          { title: '姓名', dataIndex: 'full_name' },
          { title: '角色', dataIndex: 'role', render: (r: Role) => <Tag>{r}</Tag> },
          { title: '状态', dataIndex: 'is_active', render: (v: boolean) => v ? <Tag color='green'>启用</Tag> : <Tag color='red'>停用</Tag> },
          { title: '操作', render: (_: any, row: UserRow) => (
            <Space>
              <Button onClick={() => onEdit(row)}>编辑</Button>
              <Button danger onClick={() => onDelete(row)}>删除</Button>
            </Space>
          ) }
        ]} />
      </Card>

      <Modal title={`编辑用户 #${editing?.id}`} open={!!editing} onOk={onSave} onCancel={() => setEditing(null)}>
        <Form form={editForm} labelCol={{ span: 5 }} wrapperCol={{ span: 18 }}>
          <Form.Item name="full_name" label="姓名"><Input /></Form.Item>
          <Form.Item name="password" label="新密码"><Input.Password placeholder="留空则不修改" /></Form.Item>
          <Form.Item name="role" label="角色">
            <Select options={[{value:'Operator',label:'Operator'},{value:'Reviewer',label:'Reviewer'},{value:'Admin',label:'Admin'}]} />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
