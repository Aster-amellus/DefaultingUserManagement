import { Button, Card, Form, Input, Space, Table, message } from 'antd'
import { http } from '../lib/http'
import { useEffect, useState } from 'react'

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
        ]} />
      </Card>
    </Space>
  )
}
