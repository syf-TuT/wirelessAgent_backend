<template>
  <div class="results-container">
    <div class="results-header">
      <div class="header-left">
        <el-icon class="header-icon"><data-analysis /></el-icon>
        <h3>分配结果</h3>
      </div>
      <el-tag v-if="results.length > 0" type="success" size="large" effect="dark" class="count-tag">
        共 {{ results.length }} 条记录
      </el-tag>
    </div>

    <div v-if="results.length === 0" class="empty-results">
      <el-empty description="暂无分配结果" :image-size="160">
        <template #image>
          <el-icon :size="64" color="#64748b">
            <data-analysis />
          </el-icon>
        </template>
        <template #description>
          <div class="empty-description">
            <p class="empty-main">暂无分配结果</p>
            <p class="empty-hint">请先提交用户请求进行资源分配</p>
          </div>
        </template>
      </el-empty>
    </div>

    <div v-else class="results-content">
      <el-tabs v-model="activeTab" class="results-tabs">
        <el-tab-pane name="detail">
          <template #label>
            <span class="tab-label">
              <el-icon>
                <document />
              </el-icon>
              详细数据
            </span>
          </template>
          <div class="table-wrapper">
            <el-table :data="results" stripe style="width: 100%" :row-class-name="tableRowClassName"
              :cell-class-name="tableCellClassName"
              :header-cell-style="{ background: 'rgba(15, 23, 42, 0.6)', color: '#cbd5e1', fontWeight: '600' }">
              <el-table-column prop="user_id" label="用户ID" width="100" fixed align="center">
                <template #default="{ row }">
                  <span class="user-id">{{ row.user_id }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="request" label="用户请求" min-width="280" show-overflow-tooltip>
                <template #default="{ row }">
                  <span class="request-text">{{ row.request }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="cqi" label="CQI" width="90" align="center">
                <template #default="{ row }">
                  <div class="cqi-badge" :class="getCQIClass(row.cqi)">
                    {{ row.cqi }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="slice_type" label="切片类型" width="130" align="center">
                <template #default="{ row }">
                  <div class="slice-badge" :class="getSliceClass(row.slice_type)">
                    {{ row.slice_type }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="bandwidth" label="带宽(MHz)" width="130" align="center">
                <template #default="{ row }">
                  <span class="metric-value">{{ row.bandwidth }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="rate" label="速率(Mbps)" width="130" align="center">
                <template #default="{ row }">
                  <span class="metric-value highlight">{{ row.rate }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="latency" label="延迟(ms)" width="110" align="center">
                <template #default="{ row }">
                  <span class="metric-value">{{ row.latency }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="110" align="center">
                <template #default="{ row }">
                  <div class="status-badge" :class="row.allocation_failed ? 'failed' : 'success'">
                    <el-icon>
                      <circle-check v-if="!row.allocation_failed" />
                      <circle-close v-else />
                    </el-icon>
                    <span>{{ row.allocation_failed ? '失败' : '成功' }}</span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane name="statistics">
          <template #label>
            <span class="tab-label">
              <el-icon><pie-chart /></el-icon>
              统计概览
            </span>
          </template>
          <div class="statistics-content">
            <div class="stat-section">
              <h4 class="section-title">分配状态</h4>
              <el-row :gutter="16">
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="stat-card success-card">
                    <div class="stat-icon-wrapper">
                      <el-icon class="stat-icon"><success-filled /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ successCount }}</div>
                      <div class="stat-label">成功分配</div>
                    </div>
                    <div class="stat-progress">
                      <div class="progress-bar" :style="{ width: successRate + '%' }"></div>
                    </div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="stat-card danger-card">
                    <div class="stat-icon-wrapper">
                      <el-icon class="stat-icon"><circle-close-filled /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ failedCount }}</div>
                      <div class="stat-label">分配失败</div>
                    </div>
                    <div class="stat-progress">
                      <div class="progress-bar" :style="{ width: (100 - parseFloat(successRate)) + '%' }"></div>
                    </div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="stat-card primary-card">
                    <div class="stat-icon-wrapper">
                      <el-icon class="stat-icon"><trend-charts /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ successRate }}%</div>
                      <div class="stat-label">成功率</div>
                    </div>
                    <div class="stat-progress">
                      <div class="progress-bar" :style="{ width: successRate + '%' }"></div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="stat-section">
              <h4 class="section-title">切片分布</h4>
              <el-row :gutter="16">
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="stat-card embb-card">
                    <div class="stat-icon-wrapper">
                      <el-icon class="stat-icon">
                        <monitor />
                      </el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ embbCount }}</div>
                      <div class="stat-label">eMBB切片</div>
                    </div>
                    <div class="stat-progress">
                      <div class="progress-bar" :style="{ width: (embbCount / results.length * 100) + '%' }"></div>
                    </div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="stat-card urllc-card">
                    <div class="stat-icon-wrapper">
                      <el-icon class="stat-icon">
                        <lightning />
                      </el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ urllcCount }}</div>
                      <div class="stat-label">URLLC切片</div>
                    </div>
                    <div class="stat-progress">
                      <div class="progress-bar" :style="{ width: (urllcCount / results.length * 100) + '%' }"></div>
                    </div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <div class="stat-card mmtc-card">
                    <div class="stat-icon-wrapper">
                      <el-icon class="stat-icon">
                        <connection />
                      </el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ mmtcCount }}</div>
                      <div class="stat-label">mMTC切片</div>
                    </div>
                    <div class="stat-progress">
                      <div class="progress-bar" :style="{ width: (mmtcCount / results.length * 100) + '%' }"></div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="stat-section">
              <h4 class="section-title">性能指标</h4>
              <el-row :gutter="16">
                <el-col :xs="24" :sm="12">
                  <div class="stat-card info-card">
                    <div class="stat-icon-wrapper">
                      <el-icon class="stat-icon"><data-line /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ avgRate.toFixed(2) }}</div>
                      <div class="stat-label">平均速率(Mbps)</div>
                    </div>
                  </div>
                </el-col>
                <el-col :xs="24" :sm="12">
                  <div class="stat-card warning-card">
                    <div class="stat-icon-wrapper">
                      <el-icon class="stat-icon"><warning-filled /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ adjustedCount }}</div>
                      <div class="stat-label">动态调整次数</div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="results-footer">
        <el-button size="large" @click="clearResults" class="action-button">
          <el-icon>
            <delete />
          </el-icon>
          清空结果
        </el-button>
        <el-button type="primary" size="large" @click="exportResults" class="action-button primary">
          <el-icon>
            <download />
          </el-icon>
          导出结果
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  SuccessFilled,
  CircleCloseFilled,
  TrendCharts,
  Monitor,
  Lightning,
  Connection,
  DataLine,
  WarningFilled,
  Download,
  Delete,
  Document,
  PieChart,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'

interface AllocationResult {
  user_id: string
  request: string
  cqi: number
  slice_type: string
  bandwidth: number
  rate: number
  latency: number
  allocation_failed: boolean
  adjustments_made: boolean
}

const props = defineProps<{
  results: AllocationResult[]
}>()

const emit = defineEmits<{
  export: []
  clear: []
}>()

const activeTab = ref('detail')

const successCount = computed(() => props.results.filter(r => !r.allocation_failed).length)
const failedCount = computed(() => props.results.filter(r => r.allocation_failed).length)
const successRate = computed(() => {
  if (props.results.length === 0) return 0
  return ((successCount.value / props.results.length) * 100).toFixed(1)
})

const embbCount = computed(() => props.results.filter(r => r.slice_type === 'eMBB').length)
const urllcCount = computed(() => props.results.filter(r => r.slice_type === 'URLLC').length)
const mmtcCount = computed(() => props.results.filter(r => r.slice_type === 'mMTC').length)

const avgRate = computed(() => {
  const validResults = props.results.filter(r => r.rate && !r.allocation_failed)
  if (validResults.length === 0) return 0
  const sum = validResults.reduce((acc, r) => acc + r.rate, 0)
  return sum / validResults.length
})

const adjustedCount = computed(() => props.results.filter(r => r.adjustments_made).length)

const getCQIClass = (cqi: number) => {
  if (cqi >= 12) return 'excellent'
  if (cqi >= 8) return 'good'
  return 'poor'
}

const getSliceClass = (sliceType: string) => {
  const typeMap: Record<string, string> = {
    'eMBB': 'embb',
    'URLLC': 'urllc',
    'mMTC': 'mmtc'
  }
  return typeMap[sliceType] || 'default'
}

const tableRowClassName = ({ row }: { row: AllocationResult }) => {
  if (row.allocation_failed) return 'failed-row'
  return ''
}

const tableCellClassName = ({ column, row }: { column: any; row: AllocationResult }) => {
  if (column.property === 'rate' && !row.allocation_failed) return 'rate-cell'
  return ''
}

const exportResults = () => {
  const headers = ['用户ID', '用户请求', 'CQI', '切片类型', '带宽(MHz)', '速率(Mbps)', '延迟(ms)', '状态']
  const rows = props.results.map(r => [
    r.user_id,
    r.request,
    r.cqi,
    r.slice_type,
    r.bandwidth,
    r.rate,
    r.latency,
    r.allocation_failed ? '失败' : '成功'
  ])

  let csv = headers.join(',') + '\n'
  rows.forEach(row => {
    csv += row.map(cell => `"${cell}"`).join(',') + '\n'
  })

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `allocation_results_${new Date().getTime()}.csv`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('结果已导出')
  emit('export')
}

const clearResults = () => {
  emit('clear')
}
</script>

<style scoped>
.results-container {
  background: transparent;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.results-header {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: #fff;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
  animation: pulse 2.5s ease-in-out infinite;
}

@keyframes pulse {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }
}

.results-header h3 {
  margin: 0;
  font-size: 19px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.count-tag {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #fff;
  font-weight: 600;
  backdrop-filter: blur(8px);
}

.empty-results {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px;
}

.empty-description {
  text-align: center;
}

.empty-main {
  margin: 0 0 8px 0;
  font-size: 17px;
  color: #cbd5e1;
  font-weight: 500;
}

.empty-hint {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.results-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.results-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

:deep(.el-tabs) {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding: 18px 20px;
  min-height: 0;
}

:deep(.el-tabs__content::-webkit-scrollbar) {
  width: 8px;
}

:deep(.el-tabs__content::-webkit-scrollbar-track) {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 4px;
}

:deep(.el-tabs__content::-webkit-scrollbar-thumb) {
  background: rgba(99, 102, 241, 0.4);
  border-radius: 4px;
  transition: background 0.3s ease;
}

:deep(.el-tabs__content::-webkit-scrollbar-thumb:hover) {
  background: rgba(99, 102, 241, 0.6);
}

:deep(.el-tabs__header) {
  margin: 0;
  padding: 0 20px;
  background: rgba(15, 23, 42, 0.4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(255, 255, 255, 0.06);
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  padding: 0 24px;
  height: 50px;
  line-height: 50px;
  color: #64748b;
}

:deep(.el-tabs__item:hover) {
  color: #e2e8f0;
}

:deep(.el-tabs__item.is-active) {
  color: #6366f1;
}

:deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
  height: 3px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

:deep(.el-tab-pane) {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.table-wrapper {
  background: rgba(15, 23, 42, 0.4);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

:deep(.el-table) {
  border-radius: 12px;
  background: transparent;
  flex: 1;
}

:deep(.el-table__inner-wrapper) {
  display: flex;
  flex-direction: column;
}

:deep(.el-table__body-wrapper) {
  overflow-y: auto;
  flex: 1;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar) {
  width: 8px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 4px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
  background: rgba(99, 102, 241, 0.4);
  border-radius: 4px;
  transition: background 0.3s ease;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb:hover) {
  background: rgba(99, 102, 241, 0.6);
}

:deep(.el-table__header-wrapper) {
  border-radius: 12px 12px 0 0;
}

:deep(.el-table th) {
  background: transparent !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 12px 0;
  background: transparent;
}

:deep(.el-table__body tr:hover > td) {
  background: rgba(51, 65, 85, 0.5) !important;
}

:deep(.el-table .failed-row) {
  background: rgba(239, 68, 68, 0.08);
}

:deep(.el-table .failed-row:hover > td) {
  background: rgba(239, 68, 68, 0.12) !important;
}

:deep(.el-table .rate-cell) {
  color: #818cf8;
  font-weight: 700;
}

.user-id {
  font-weight: 600;
  color: #e2e8f0;
  font-family: 'SF Mono', 'Consolas', 'Courier New', monospace;
}

.request-text {
  color: #cbd5e1;
  font-size: 14px;
}

.cqi-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
  transition: all 0.3s ease;
}

.cqi-badge.excellent {
  background: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
}

.cqi-badge.good {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.cqi-badge.poor {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.slice-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.slice-badge.embb {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.slice-badge.urllc {
  background: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
}

.slice-badge.mmtc {
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.3);
}

.slice-badge.default {
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
}

.metric-value {
  font-weight: 500;
  color: #e2e8f0;
  font-size: 15px;
}

.metric-value.highlight {
  color: #818cf8;
  font-weight: 700;
  font-size: 16px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.3s ease;
}

.status-badge.success {
  background: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
}

.status-badge.failed {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.statistics-content {
  padding: 0;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.statistics-content::-webkit-scrollbar {
  width: 8px;
}

.statistics-content::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 4px;
}

.statistics-content::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.4);
  border-radius: 4px;
  transition: background 0.3s ease;
}

.statistics-content::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.6);
}

.stat-section {
  margin-bottom: 28px;
}

.stat-section:last-child {
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 18px 0;
  font-size: 16px;
  font-weight: 600;
  color: #e2e8f0;
  padding-left: 12px;
  border-left: 4px solid #6366f1;
}

.stat-card {
  background: rgba(30, 41, 59, 0.7);
  border-radius: 16px;
  padding: 22px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  margin-bottom: 16px;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
  opacity: 0;
  transition: opacity 0.35s ease;
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.12);
}

.stat-card.success-card::before {
  background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
}

.stat-card.danger-card::before {
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
}

.stat-card.primary-card::before {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.stat-card.embb-card::before {
  background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
}

.stat-card.urllc-card::before {
  background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
}

.stat-card.mmtc-card::before {
  background: linear-gradient(90deg, #64748b 0%, #94a3b8 100%);
}

.stat-card.info-card::before {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.stat-card.warning-card::before {
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.stat-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.stat-icon {
  font-size: 30px;
  color: #fff;
}

.stat-card.success-card .stat-icon-wrapper {
  background: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.stat-card.danger-card .stat-icon-wrapper {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.stat-card.primary-card .stat-icon-wrapper {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.stat-card.embb-card .stat-icon-wrapper {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.stat-card.urllc-card .stat-icon-wrapper {
  background: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.stat-card.mmtc-card .stat-icon-wrapper {
  background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.3);
}

.stat-card.info-card .stat-icon-wrapper {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.stat-card.warning-card .stat-icon-wrapper {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.stat-content {
  margin-bottom: 14px;
}

.stat-value {
  font-size: 30px;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.stat-progress {
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
  border-radius: 3px;
  transition: width 0.6s ease;
}

.stat-card.success-card .progress-bar {
  background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
}

.stat-card.danger-card .progress-bar {
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
}

.stat-card.primary-card .progress-bar {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.stat-card.embb-card .progress-bar {
  background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
}

.stat-card.urllc-card .progress-bar {
  background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
}

.stat-card.mmtc-card .progress-bar {
  background: linear-gradient(90deg, #64748b 0%, #94a3b8 100%);
}

.stat-card.info-card .progress-bar {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.stat-card.warning-card .progress-bar {
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.results-footer {
  padding: 18px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background: rgba(15, 23, 42, 0.4);
}

.action-button {
  border-radius: 10px;
  padding: 12px 28px;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.1);
}

.action-button.primary {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border: none;
  color: #fff;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.action-button.primary:hover {
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.action-button:active {
  transform: translateY(0);
}
</style>
