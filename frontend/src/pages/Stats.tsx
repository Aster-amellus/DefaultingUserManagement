import ReactECharts from 'echarts-for-react'
import { Card, DatePicker, Space, message, Row, Col } from 'antd'
import { useEffect, useState } from 'react'
import { http } from '../lib/http'

type IndustryStat = {
  industry: string
  default_count: number
  rebirth_count: number
  default_share?: number
  rebirth_share?: number
  default_trend?: number[]
  rebirth_trend?: number[]
}
type RegionStat = {
  region: string
  default_count: number
  rebirth_count: number
  default_share?: number
  rebirth_share?: number
  default_trend?: number[]
  rebirth_trend?: number[]
}

export default function Stats() {
  const [year, setYear] = useState<number>(new Date().getFullYear())
  const [industry, setIndustry] = useState<IndustryStat[]>([])
  const [region, setRegion] = useState<RegionStat[]>([])

  const load = async (y: number) => {
    try {
      const [i, r] = await Promise.all([
        http.get<IndustryStat[]>('/stats/industry', { params: { year: y, detailed: true } }),
        http.get<RegionStat[]>('/stats/region', { params: { year: y, detailed: true } }),
      ])
      setIndustry(i.data as IndustryStat[])
      setRegion(r.data as RegionStat[])
    } catch { message.error('统计获取失败') }
  }

  useEffect(() => { load(year) }, [year])

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
  <DatePicker picker="year" onChange={(d)=> setYear(d?.year() ?? year)} />

      <Card title="按行业统计">
        <Row gutter={16}>
          <Col span={24}>
            <ReactECharts style={{ height: 320 }} option={{
              tooltip: {},
              xAxis: { type: 'category', data: industry.map((i)=>i.industry) },
              yAxis: { type: 'value' },
              legend: { data: ['违约', '重生'] },
              series: [
                { type: 'bar', name: '违约', data: industry.map((i)=>i.default_count) },
                { type: 'bar', name: '重生', data: industry.map((i)=>i.rebirth_count) },
              ]
            }} />
          </Col>
          <Col span={12}>
            <ReactECharts style={{ height: 320 }} option={{
              title: { text: '行业占比（违约）', left: 'center' },
              tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
              series: [{
                type: 'pie', radius: '60%',
                data: industry.map(i => ({ name: i.industry, value: (i.default_share ?? 0) * 100 }))
              }]
            }} />
          </Col>
          <Col span={12}>
            <ReactECharts style={{ height: 320 }} option={{
              title: { text: '行业占比（重生）', left: 'center' },
              tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
              series: [{
                type: 'pie', radius: '60%',
                data: industry.map(i => ({ name: i.industry, value: (i.rebirth_share ?? 0) * 100 }))
              }]
            }} />
          </Col>
          <Col span={24}>
            <ReactECharts style={{ height: 360 }} option={{
              title: { text: '月度趋势（违约）' },
              tooltip: { trigger: 'axis' },
              legend: { type: 'scroll' },
              xAxis: { type: 'category', data: Array.from({length:12},(_,i)=>`${i+1}月`) },
              yAxis: { type: 'value' },
              series: industry.map(i => ({ type: 'line', name: i.industry, data: i.default_trend ?? Array(12).fill(0) }))
            }} />
          </Col>
          <Col span={24}>
            <ReactECharts style={{ height: 360 }} option={{
              title: { text: '月度趋势（重生）' },
              tooltip: { trigger: 'axis' },
              legend: { type: 'scroll' },
              xAxis: { type: 'category', data: Array.from({length:12},(_,i)=>`${i+1}月`) },
              yAxis: { type: 'value' },
              series: industry.map(i => ({ type: 'line', name: i.industry, data: i.rebirth_trend ?? Array(12).fill(0) }))
            }} />
          </Col>
        </Row>
      </Card>

      <Card title="按区域统计">
        <Row gutter={16}>
          <Col span={24}>
            <ReactECharts style={{ height: 320 }} option={{
              tooltip: {},
              xAxis: { type: 'category', data: region.map((i)=>i.region) },
              yAxis: { type: 'value' },
              legend: { data: ['违约', '重生'] },
              series: [
                { type: 'bar', name: '违约', data: region.map((i)=>i.default_count) },
                { type: 'bar', name: '重生', data: region.map((i)=>i.rebirth_count) },
              ]
            }} />
          </Col>
          <Col span={12}>
            <ReactECharts style={{ height: 320 }} option={{
              title: { text: '区域占比（违约）', left: 'center' },
              tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
              series: [{
                type: 'pie', radius: '60%',
                data: region.map(i => ({ name: i.region, value: (i.default_share ?? 0) * 100 }))
              }]
            }} />
          </Col>
          <Col span={12}>
            <ReactECharts style={{ height: 320 }} option={{
              title: { text: '区域占比（重生）', left: 'center' },
              tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
              series: [{
                type: 'pie', radius: '60%',
                data: region.map(i => ({ name: i.region, value: (i.rebirth_share ?? 0) * 100 }))
              }]
            }} />
          </Col>
          <Col span={24}>
            <ReactECharts style={{ height: 360 }} option={{
              title: { text: '月度趋势（违约）' },
              tooltip: { trigger: 'axis' },
              legend: { type: 'scroll' },
              xAxis: { type: 'category', data: Array.from({length:12},(_,i)=>`${i+1}月`) },
              yAxis: { type: 'value' },
              series: region.map(i => ({ type: 'line', name: i.region, data: i.default_trend ?? Array(12).fill(0) }))
            }} />
          </Col>
          <Col span={24}>
            <ReactECharts style={{ height: 360 }} option={{
              title: { text: '月度趋势（重生）' },
              tooltip: { trigger: 'axis' },
              legend: { type: 'scroll' },
              xAxis: { type: 'category', data: Array.from({length:12},(_,i)=>`${i+1}月`) },
              yAxis: { type: 'value' },
              series: region.map(i => ({ type: 'line', name: i.region, data: i.rebirth_trend ?? Array(12).fill(0) }))
            }} />
          </Col>
        </Row>
      </Card>
    </Space>
  )
}
