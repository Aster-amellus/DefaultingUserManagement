import { Button, Card, Form, Input, Radio, Space, Switch, Table, message, Modal, Popconfirm } from 'antd'
import { http } from '../lib/http'
import { useEffect, useState } from 'react'
import { useAuthStore } from '../stores/auth'

type Reason = { id: number, type: 'DEFAULT'|'REBIRTH', description: string, enabled: boolean, sort_order: number }

export default function Reasons() {
  const [data, setData] = useState<Reason[]>([])
  const [loading, setLoading] = useState(false)
  const role = useAuthStore(s => s.role)
  const [editing, setEditing] = useState<Reason | null>(null)
  const [editForm] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
  const { data } = await http.get('/reasons/')
      setData(data)
    } catch {
      message.error('加载失败')
    } finally { setLoading(false) }
  }
  useEffect(() => { fetchData() }, [])

  const onCreate = async (v: any) => {
    try {
  await http.post('/reasons/', v)
      message.success('已创建')
      fetchData()
    } catch { message.error('创建失败') }
  }

  const onToggle = async (r: Reason) => {
    try {
  await http.patch(`/reasons/${r.id}`, { ...r, enabled: !r.enabled })
      fetchData()
    } catch { message.error('更新失败') }
  }

  const onEdit = (r: Reason) => {
    setEditing(r)
    editForm.setFieldsValue({ ...r })
  }

  const onSave = async () => {
    const v = await editForm.validateFields()
    try {
      await http.patch(`/reasons/${editing!.id}`, v)
      message.success('已保存')
      setEditing(null)
      fetchData()
    } catch { message.error('保存失败') }
  }

  const onDelete = async (r: Reason) => {
    try {
      await http.delete(`/reasons/${r.id}`)
      message.success('已删除')
      fetchData()
    } catch { message.error('删除失败') }
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Card title="新建原因">
        <Form layout="inline" onFinish={onCreate} initialValues={{ enabled: true, sort_order: 1 }}>
          <Form.Item name="type" label="类型" rules={[{ required: true }]}>
            <Radio.Group>
              <Radio.Button value="DEFAULT">违约</Radio.Button>
              <Radio.Button value="REBIRTH">重生</Radio.Button>
            </Radio.Group>
          </Form.Item>
          <Form.Item name="description" label="描述" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="sort_order" label="排序" rules={[{ required: true }]}><Input type="number" /></Form.Item>
          <Form.Item name="enabled" label="启用" valuePropName="checked"><Switch /></Form.Item>
          <Button type="primary" htmlType="submit">创建</Button>
        </Form>
      </Card>

      <Card title="原因列表">
        <Table rowKey="id" loading={loading} dataSource={data} columns={[
          { title: '类型', dataIndex: 'type' },
          { title: '描述', dataIndex: 'description' },
          { title: '启用', dataIndex: 'enabled', render: (_, r: Reason) => <Switch checked={r.enabled} onChange={() => onToggle(r)} /> },
          { title: '排序', dataIndex: 'sort_order' },
          ...(role === 'Admin' ? [{
            title: '操作',
            render: (_: any, r: Reason) => (
              <Space>
                <Button onClick={() => onEdit(r)}>编辑</Button>
                <Popconfirm title="确认删除？" onConfirm={() => onDelete(r)}>
                  <Button danger>删除</Button>
                </Popconfirm>
              </Space>
            )
          }] : [] as any)
        ]} />
      </Card>

      <Modal title={`编辑原因 #${editing?.id}`} open={!!editing} onOk={onSave} onCancel={() => setEditing(null)}>
        <Form form={editForm} labelCol={{ span: 5 }} wrapperCol={{ span: 18 }}>
          <Form.Item name="type" label="类型" rules={[{ required: true }]}>
            <Radio.Group>
              <Radio.Button value="DEFAULT">违约</Radio.Button>
              <Radio.Button value="REBIRTH">重生</Radio.Button>
            </Radio.Group>
          </Form.Item>
          <Form.Item name="description" label="描述" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="sort_order" label="排序" rules={[{ required: true }]}><Input type="number" /></Form.Item>
          <Form.Item name="enabled" label="启用" valuePropName="checked"><Switch /></Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
