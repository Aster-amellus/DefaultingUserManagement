import { Button, Card, Form, Input, Modal, Popconfirm, Space, Table, message } from 'antd'
import { http } from '../lib/http'
import { useEffect, useState } from 'react'
import { useAuthStore } from '../stores/auth'

interface Customer {
  id: number
  name: string
  industry?: string
  region?: string
  is_default: boolean
}

export default function Customers() {
  const [data, setData] = useState<Customer[]>([])
  const [loading, setLoading] = useState(false)
  const role = useAuthStore(s => s.role)
  const [editing, setEditing] = useState<Customer | null>(null)
  const [editForm] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
  const { data } = await http.get('/customers/')
      setData(data)
    } catch {
      message.error('加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const onCreate = async (v: any) => {
    try {
  await http.post('/customers/', v)
      message.success('已创建')
      fetchData()
    } catch {
      message.error('创建失败')
    }
  }

  const onEdit = (row: Customer) => {
    setEditing(row)
    editForm.setFieldsValue({ ...row })
  }

  const onSave = async () => {
    const v = await editForm.validateFields()
    try {
      await http.patch(`/customers/${editing!.id}`, v)
      message.success('已保存')
      setEditing(null)
      fetchData()
    } catch (e: any) { message.error(e?.response?.data?.detail || '保存失败') }
  }

  const onDelete = async (row: Customer) => {
    try {
      await http.delete(`/customers/${row.id}`)
      message.success('已删除')
      fetchData()
    } catch { message.error('删除失败') }
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Card title="新建客户">
        <Form layout="inline" onFinish={onCreate}>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="industry" label="行业"><Input /></Form.Item>
          <Form.Item name="region" label="区域"><Input /></Form.Item>
          <Button type="primary" htmlType="submit">创建</Button>
        </Form>
      </Card>

      <Card title="客户列表">
        <Table rowKey="id" loading={loading} dataSource={data} columns={[
          { title: '名称', dataIndex: 'name' },
          { title: '行业', dataIndex: 'industry' },
          { title: '区域', dataIndex: 'region' },
          { title: '违约', dataIndex: 'is_default', render: (v) => v ? '是' : '否' },
          ...(role === 'Admin' ? [{
            title: '操作', render: (_: any, row: Customer) => (
              <Space>
                <Button onClick={() => onEdit(row)}>编辑</Button>
                <Popconfirm title="确认删除？" onConfirm={() => onDelete(row)}>
                  <Button danger>删除</Button>
                </Popconfirm>
              </Space>
            )
          }] : [] as any)
        ]} />
      </Card>

      <Modal title={`编辑客户 #${editing?.id}`} open={!!editing} onOk={onSave} onCancel={() => setEditing(null)}>
        <Form form={editForm} labelCol={{ span: 5 }} wrapperCol={{ span: 18 }}>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}><Input disabled={role!=='Admin'} /></Form.Item>
          <Form.Item name="industry" label="行业"><Input /></Form.Item>
          <Form.Item name="region" label="区域"><Input /></Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
