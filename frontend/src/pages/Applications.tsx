import { Button, Card, Form, Input, Radio, Select, Space, Table, Tag, Upload, message } from 'antd'
import { http } from '../lib/http'
import { useEffect, useMemo, useState } from 'react'

interface Reason { id: number, type: 'DEFAULT'|'REBIRTH', description: string, enabled: boolean }
interface Customer { id: number, name: string, is_default: boolean }
interface Application {
  id: number
  type: 'DEFAULT'|'REBIRTH'
  customer_id: number
  latest_external_rating?: string
  reason_id: number
  severity?: 'HIGH'|'MEDIUM'|'LOW'
  remark?: string
  status: 'PENDING'|'APPROVED'|'REJECTED'
}

export default function Applications() {
  const [reasons, setReasons] = useState<Reason[]>([])
  const [customers, setCustomers] = useState<Customer[]>([])
  const [apps, setApps] = useState<Application[]>([])
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const [rs, cs, as] = await Promise.all([
        http.get('/reasons/'),
        http.get('/customers/'),
        http.get('/applications/')
      ])
      setReasons(rs.data)
      setCustomers(cs.data)
      setApps(as.data)
    } catch { message.error('加载失败') } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const onSubmit = async (v: any) => {
    try {
  await http.post('/applications/', v)
      message.success('已提交')
      load()
    } catch { message.error('提交失败') }
  }

  const onReview = async (id: number, decision: 'APPROVED'|'REJECTED') => {
    try {
  await http.post(`/applications/${id}/review`, { decision })
      message.success('已审核')
      load()
    } catch { message.error('审核失败') }
  }

  const uploadProps = (appId: number) => ({
    name: 'file',
    customRequest: async (e: any) => {
      const form = new FormData()
      form.append('file', e.file)
  await http.post(`/applications/${appId}/attachments`, form)
      e.onSuccess({}, e.file)
    }
  })

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Card title="发起申请">
        <Form layout="inline" onFinish={onSubmit} initialValues={{ type: 'DEFAULT', severity: 'MEDIUM' }}>
          <Form.Item name="type" label="类型" rules={[{ required: true }]}>
            <Radio.Group>
              <Radio.Button value="DEFAULT">违约</Radio.Button>
              <Radio.Button value="REBIRTH">重生</Radio.Button>
            </Radio.Group>
          </Form.Item>
          <Form.Item name="customer_id" label="客户" rules={[{ required: true }]}>
            <Select style={{ width: 200 }} options={customers.map(c => ({ label: c.name, value: c.id }))} />
          </Form.Item>
          <Form.Item name="reason_id" label="原因" rules={[{ required: true }]}>
            <Select style={{ width: 240 }} options={reasons.filter(r => r.enabled).map(r => ({ label: `${r.type==='DEFAULT'?'违约':'重生'}-${r.description}`, value: r.id }))} />
          </Form.Item>
          <Form.Item name="latest_external_rating" label="评级"><Input style={{ width: 120 }} /></Form.Item>
          <Form.Item name="severity" label="严重性">
            <Select style={{ width: 140 }} options={[{ value: 'HIGH', label: '高' }, { value: 'MEDIUM', label: '中' }, { value: 'LOW', label: '低' }]} />
          </Form.Item>
          <Form.Item name="remark" label="备注"><Input style={{ width: 240 }} /></Form.Item>
          <Button type="primary" htmlType="submit">提交</Button>
        </Form>
      </Card>

      <Card title="申请列表">
        <Table rowKey="id" loading={loading} dataSource={apps} columns={[
          { title: '类型', dataIndex: 'type', render: (v) => v==='DEFAULT'?'违约':'重生' },
          { title: '客户', dataIndex: 'customer_id', render: (id) => customers.find(c=>c.id===id)?.name },
          { title: '原因', dataIndex: 'reason_id', render: (id) => reasons.find(r=>r.id===id)?.description },
          { title: '严重性', dataIndex: 'severity' },
          { title: '状态', dataIndex: 'status', render: (s) => <Tag color={s==='APPROVED'?'green':s==='REJECTED'?'red':'blue'}>{s}</Tag> },
          { title: '操作', render: (_, r: Application) => (
            <Space>
              <Upload {...uploadProps(r.id)} showUploadList={false}><Button>上传附件</Button></Upload>
              <Button onClick={() => onReview(r.id, 'APPROVED')}>同意</Button>
              <Button danger onClick={() => onReview(r.id, 'REJECTED')}>拒绝</Button>
            </Space>
          )}
        ]} />
      </Card>
    </Space>
  )
}
