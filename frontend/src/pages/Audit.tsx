import { Card, DatePicker, Input, Select, Space, Table, message } from 'antd'
import dayjs, { Dayjs } from 'dayjs'
import { useEffect, useState } from 'react'
import { http } from '../lib/http'

type Audit = {
  id: number
  timestamp: string
  actor?: string
  action: string
  resource?: string
  ip?: string
}

export default function Audit() {
  const [data, setData] = useState<Audit[]>([])
  const [loading, setLoading] = useState(false)
  const [actor, setActor] = useState<string>()
  const [action, setAction] = useState<string>()
  const [from, setFrom] = useState<Dayjs | null>()
  const [to, setTo] = useState<Dayjs | null>()

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await http.get('/audit-logs', {
        params: {
          actor,
          action,
          start: from?.toISOString(),
          end: to?.toISOString(),
        }
      })
      setData(data.items || data)
    } catch { message.error('获取失败') } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Card title="筛选">
        <Space wrap>
          <Input placeholder="操作者" value={actor} onChange={e=>setActor(e.target.value)} style={{ width: 160 }} />
          <Input placeholder="动作" value={action} onChange={e=>setAction(e.target.value)} style={{ width: 160 }} />
          <DatePicker placeholder="开始" showTime value={from||null} onChange={setFrom} />
          <DatePicker placeholder="结束" showTime value={to||null} onChange={setTo} />
          <a onClick={load}>查询</a>
        </Space>
      </Card>

      <Card title="审计日志">
        <Table rowKey="id" loading={loading} dataSource={data} columns={[
          { title: '时间', dataIndex: 'timestamp', render: (v: string) => dayjs(v).format('YYYY-MM-DD HH:mm:ss') },
          { title: '操作者', dataIndex: 'actor' },
          { title: '动作', dataIndex: 'action' },
          { title: '资源', dataIndex: 'resource' },
          { title: 'IP', dataIndex: 'ip' },
        ]} />
      </Card>
    </Space>
  )
}
