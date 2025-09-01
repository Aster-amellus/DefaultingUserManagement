import ReactECharts from 'echarts-for-react'
import { Card, DatePicker, Space, message } from 'antd'
import { useEffect, useState } from 'react'
import { http } from '../lib/http'

type IndustryStat = { industry: string; default_count: number; rebirth_count: number }
type RegionStat = { region: string; default_count: number; rebirth_count: number }

export default function Stats() {
  const [year, setYear] = useState<number>(new Date().getFullYear())
  const [industry, setIndustry] = useState<IndustryStat[]>([])
  const [region, setRegion] = useState<RegionStat[]>([])

  const load = async (y: number) => {
    try {
      const [i, r] = await Promise.all([
        http.get<IndustryStat[]>('/stats/industry', { params: { year: y } }),
        http.get<RegionStat[]>('/stats/region', { params: { year: y } }),
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
        <ReactECharts style={{ height: 360 }} option={{
          tooltip: {},
          xAxis: { type: 'category', data: industry.map((i: IndustryStat)=>i.industry) },
          yAxis: { type: 'value' },
          series: [
            { type: 'bar', name: '违约', data: industry.map((i: IndustryStat)=>i.default_count) },
            { type: 'bar', name: '重生', data: industry.map((i: IndustryStat)=>i.rebirth_count) },
          ]
        }} />
      </Card>

      <Card title="按区域统计">
        <ReactECharts style={{ height: 360 }} option={{
          tooltip: {},
          xAxis: { type: 'category', data: region.map((i: RegionStat)=>i.region) },
          yAxis: { type: 'value' },
          series: [
            { type: 'bar', name: '违约', data: region.map((i: RegionStat)=>i.default_count) },
            { type: 'bar', name: '重生', data: region.map((i: RegionStat)=>i.rebirth_count) },
          ]
        }} />
      </Card>
    </Space>
  )
}
