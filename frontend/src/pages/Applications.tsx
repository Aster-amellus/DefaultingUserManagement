import { Button, Card, Form, Input, Radio, Select, Space, Table, Tag, Upload, message, Popconfirm } from 'antd'
import { http } from '../lib/http'
import { useAuthStore } from '../stores/auth'
import { useEffect, useMemo, useState } from 'react'

interface Reason { id: number, type: 'DEFAULT'|'REBIRTH', description: string, enabled: boolean }
interface Customer { id: number, name: string, is_default: boolean }
interface ApplicationRow {
  id: number
  type: 'DEFAULT'|'REBIRTH'
  status: 'PENDING'|'APPROVED'|'REJECTED'
  severity?: 'HIGH'|'MEDIUM'|'LOW'
  latest_external_rating?: string
  remark?: string
  customer_id: number
  customer_name: string
  reason_id: number
  reason_description: string
  created_by: number
  created_by_name?: string
  reviewed_by?: number
  reviewed_by_name?: string
  created_at: string
  reviewed_at?: string
}

export default function Applications() {
  const role = useAuthStore(s => s.role)
  const userId = useAuthStore(s => s.userId)
  const [reasons, setReasons] = useState<Reason[]>([])
  const [customers, setCustomers] = useState<Customer[]>([])
  const [apps, setApps] = useState<ApplicationRow[]>([])
  const [loading, setLoading] = useState(false)
  const [searchForm] = Form.useForm()
  const [createForm] = Form.useForm()
  const [createFiles, setCreateFiles] = useState<any[]>([])

  const load = async () => {
    setLoading(true)
    try {
      const [rs, cs, as] = await Promise.all([
        http.get('/reasons/'),
        http.get('/customers/'),
        http.get('/applications/search')
      ])
      setReasons(rs.data)
      setCustomers(cs.data)
      setApps(as.data)
    } catch { message.error('加载失败') } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const onSubmit = async (v: any) => {
    try {
      const { data: created } = await http.post('/applications/', v)
      const appId = created.id
      // upload selected files if any
      if (createFiles.length > 0) {
        for (const f of createFiles) {
          const fd = new FormData()
          fd.append('file', f.originFileObj || f.file || f)
          await http.post(`/applications/${appId}/attachments`, fd)
        }
        message.success('申请与附件已提交')
      } else {
        message.success('申请已提交')
      }
      setCreateFiles([])
      load()
      createForm.resetFields()
    } catch (e: any) { message.error(e?.response?.data?.detail || '提交失败') }
  }

  const onReview = async (id: number, decision: 'APPROVED'|'REJECTED') => {
    try {
      await http.post(`/applications/${id}/review`, { decision })
      message.success('已审核')
      load()
    } catch (e: any) { message.error(e?.response?.data?.detail || '审核失败') }
  }

  const onDelete = async (id: number) => {
    try {
      await http.delete(`/applications/${id}`)
      message.success('已删除')
      load()
    } catch { message.error('删除失败') }
  }

  const uploadProps = (appId: number) => ({
    name: 'file',
    customRequest: async (e: any) => {
      try {
        const form = new FormData()
        form.append('file', e.file as File)
        await http.post(`/applications/${appId}/attachments`, form)
        message.success('已上传附件')
        e.onSuccess({}, e.file)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || '上传失败'
        message.error(msg)
        e.onError?.(err)
      }
    }
  })

  const typeWatch: 'DEFAULT'|'REBIRTH' = Form.useWatch('type', createForm) || 'DEFAULT'
  const filteredReasons = useMemo(() => reasons.filter(r => r.enabled && r.type === typeWatch), [reasons, typeWatch])
  const filteredCustomers = useMemo(() => customers.filter(c => (typeWatch === 'DEFAULT' ? !c.is_default : c.is_default)), [customers, typeWatch])

  const doSearch = async () => {
    const v = await searchForm.getFieldsValue()
    setLoading(true)
    try {
      const res = await http.get('/applications/search', { params: v })
      setApps(res.data)
    } finally { setLoading(false) }
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
  {role !== 'Reviewer' && (
  <Card title="发起申请">
        <Form layout="inline" form={createForm} onFinish={onSubmit} initialValues={{ type: 'DEFAULT', severity: 'MEDIUM' }}>
          <Form.Item name="type" label="类型" rules={[{ required: true }]}>
            <Radio.Group>
              <Radio.Button value="DEFAULT">违约</Radio.Button>
              <Radio.Button value="REBIRTH">重生</Radio.Button>
            </Radio.Group>
          </Form.Item>
          <Form.Item name="customer_id" label="客户" rules={[{ required: true }]}>            
            <Select style={{ width: 200 }} options={filteredCustomers.map(c => ({ label: c.name, value: c.id }))} />
          </Form.Item>
          <Form.Item name="reason_id" label="原因" rules={[{ required: true }]}>            
            <Select style={{ width: 320 }} options={filteredReasons.map(r => ({ label: r.description, value: r.id }))} />          
          </Form.Item>
          <Form.Item name="latest_external_rating" label="评级"><Input style={{ width: 120 }} /></Form.Item>
          <Form.Item name="severity" label="严重性">
            <Select style={{ width: 140 }} options={[{ value: 'HIGH', label: '高' }, { value: 'MEDIUM', label: '中' }, { value: 'LOW', label: '低' }]} />
          </Form.Item>
          <Form.Item name="remark" label="备注"><Input style={{ width: 240 }} /></Form.Item>
          <Form.Item label="附件">
            <Upload
              multiple
              fileList={createFiles}
              beforeUpload={() => false}
              onChange={({ fileList }) => setCreateFiles(fileList)}
              showUploadList
            >
              <Button>选择文件</Button>
            </Upload>
          </Form.Item>
          <Button type="primary" htmlType="submit">提交</Button>
        </Form>
      </Card>
      )}

      <Card title="申请列表">
        <Form layout="inline" form={searchForm} onFinish={doSearch} style={{ marginBottom: 12 }}>
          <Form.Item name="customer_name" label="客户"><Input placeholder="模糊搜索" /></Form.Item>
          <Form.Item name="status" label="状态">
            <Select allowClear style={{ width: 160 }} options={[
              { value: 'PENDING', label: '待审核' },
              { value: 'APPROVED', label: '同意' },
              { value: 'REJECTED', label: '拒绝' },
            ]} />
          </Form.Item>
          <Form.Item name="type" label="类型">
            <Select allowClear style={{ width: 160 }} options={[
              { value: 'DEFAULT', label: '违约' },
              { value: 'REBIRTH', label: '重生' },
            ]} />
          </Form.Item>
          <Button type="primary" htmlType="submit">查询</Button>
          <Button onClick={load} style={{ marginLeft: 8 }}>重置</Button>
        </Form>
        <Table rowKey="id" loading={loading} dataSource={apps} columns={[
          { title: '类型', dataIndex: 'type', render: (v) => v==='DEFAULT'?'违约':'重生' },
          { title: '客户', dataIndex: 'customer_name' },
          { title: '原因', dataIndex: 'reason_description' },
          { title: '严重性', dataIndex: 'severity' },
          { title: '评级', dataIndex: 'latest_external_rating' },
          { title: '申请人', dataIndex: 'created_by_name' },
          { title: '申请时间', dataIndex: 'created_at' },
          { title: '审核时间', dataIndex: 'reviewed_at' },
          { title: '状态', dataIndex: 'status', render: (s) => <Tag color={s==='APPROVED'?'green':s==='REJECTED'?'red':'blue'}>{s}</Tag> },
          { title: '操作', render: (_: any, r: ApplicationRow) => {
            const canUpload = r.status === 'PENDING' && (role === 'Admin' || r.created_by === userId)
            const canReview = r.status === 'PENDING' && (role === 'Admin' || role === 'Reviewer')
            return (
              <Space>
                {canUpload && <Upload {...uploadProps(r.id)} showUploadList={false}><Button>上传附件</Button></Upload>}
                {canReview && <Button onClick={() => onReview(r.id, 'APPROVED')}>同意</Button>}
                {canReview && <Button danger onClick={() => onReview(r.id, 'REJECTED')}>拒绝</Button>}
                {role === 'Admin' && (
                  <Popconfirm title="确认删除该申请？" onConfirm={() => onDelete(r.id)}>
                    <Button danger>删除</Button>
                  </Popconfirm>
                )}
              </Space>
            )
          }}
        ]} />
      </Card>
    </Space>
  )
}
