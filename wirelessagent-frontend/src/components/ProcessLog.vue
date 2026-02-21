<template>
  <div class="process-log-container">
    <div class="log-header">
      <div class="header-left">
        <el-icon class="header-icon"><document /></el-icon>
        <h3>处理日志</h3>
        <el-badge :value="logCount" class="log-count" />
      </div>
    </div>

    <div class="log-filter">
      <div class="filter-buttons">
        <el-button
          v-for="filter in filterOptions"
          :key="filter.value"
          size="small"
          :type="activeFilter === filter.value ? 'primary' : ''"
          @click="activeFilter = filter.value"
          :class="['filter-btn', `filter-${filter.value}`]"
        >
          <el-icon>
            <component :is="filter.icon" />
          </el-icon>
          {{ filter.label }}
        </el-button>
      </div>
    </div>

    <div class="log-content" ref="logContentRef">
      <transition-group name="log-item">
        <div
          v-for="(log, index) in filteredLogs"
          :key="index"
          :class="['log-item', `log-${log.type}`]"
        >
          <el-icon class="log-icon">
            <component :is="getLogIcon(log.type)" />
          </el-icon>
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </transition-group>

      <div v-if="filteredLogs.length === 0" class="empty-log">
        <el-empty description="暂无日志" :image-size="100">
          <template #image>
            <el-icon :size="40" color="#64748b">
              <document />
            </el-icon>
          </template>
        </el-empty>
      </div>
    </div>

    <div class="log-footer">
      <el-button size="small" @click="clearLogs" class="footer-btn">
        <el-icon><delete /></el-icon>
        清空日志
      </el-button>
      <el-button size="small" @click="exportLogs" class="footer-btn primary">
        <el-icon><download /></el-icon>
        导出日志
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { Document, Delete, Download, SuccessFilled, Warning, InfoFilled, CircleCloseFilled } from '@element-plus/icons-vue'

interface LogEntry {
  type: 'info' | 'success' | 'warning' | 'error'
  message: string
  time: string
}

const props = defineProps<{
  logs: LogEntry[]
}>()

const emit = defineEmits<{
  clear: []
}>()

const logContentRef = ref<HTMLElement>()
const logCount = computed(() => props.logs.length)
const activeFilter = ref<'all' | 'info' | 'success' | 'warning' | 'error'>('all')

const filterOptions = [
  { value: 'all', label: '全部', icon: Document },
  { value: 'info', label: '信息', icon: InfoFilled },
  { value: 'success', label: '成功', icon: SuccessFilled },
  { value: 'warning', label: '警告', icon: Warning },
  { value: 'error', label: '错误', icon: CircleCloseFilled }
]

const filteredLogs = computed(() => {
  if (activeFilter.value === 'all') {
    return props.logs
  }
  return props.logs.filter(log => log.type === activeFilter.value)
})

watch(() => filteredLogs.value.length, async () => {
  await nextTick()
  if (logContentRef.value) {
    logContentRef.value.scrollTop = logContentRef.value.scrollHeight
  }
})

const getLogIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    info: InfoFilled,
    success: SuccessFilled,
    warning: Warning,
    error: CircleCloseFilled
  }
  return iconMap[type] || InfoFilled
}

const clearLogs = () => {
  emit('clear')
}

const exportLogs = () => {
  const logText = props.logs
    .map(log => `[${log.time}] [${log.type.toUpperCase()}] ${log.message}`)
    .join('\n')
  
  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `process_log_${new Date().getTime()}.txt`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.process-log-container {
  background: transparent;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.log-header {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: #fff;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 20px;
}

.log-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.log-count {
  margin-left: 4px;
}

:deep(.el-badge__content) {
  background: rgba(251, 191, 36, 0.9);
  color: #1e293b;
  font-weight: 700;
  border: 1px solid rgba(251, 191, 36, 0.3);
  backdrop-filter: blur(8px);
}

.log-filter {
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.filter-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  border-radius: 20px;
  padding: 6px 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
}

.filter-btn:hover {
  border-color: rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  transform: translateY(-1px);
}

.filter-all {
  --filter-color: #6366f1;
}

.filter-info {
  --filter-color: #3b82f6;
}

.filter-success {
  --filter-color: #22c55e;
}

.filter-warning {
  --filter-color: #f59e0b;
}

.filter-error {
  --filter-color: #ef4444;
}

.filter-btn[class*="el-button--primary"] {
  background: linear-gradient(135deg, var(--filter-color) 0%, var(--filter-color) 100%);
  border-color: var(--filter-color);
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  background: rgba(15, 23, 42, 0.3);
  max-height: none;
}

.log-content::-webkit-scrollbar {
  width: 6px;
}

.log-content::-webkit-scrollbar-track {
  background: transparent;
}

.log-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.log-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.log-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  margin-bottom: 8px;
  border-radius: 10px;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.06);
  animation: slideIn 0.3s ease;
  transition: all 0.2s ease;
}

.log-item:hover {
  background: rgba(51, 65, 85, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateX(2px);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.log-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.log-info .log-icon {
  color: #3b82f6;
}

.log-success .log-icon {
  color: #22c55e;
}

.log-warning .log-icon {
  color: #f59e0b;
}

.log-error .log-icon {
  color: #ef4444;
}

.log-time {
  color: #64748b;
  font-size: 12px;
  font-family: 'SF Mono', 'Consolas', 'Courier New', monospace;
  flex-shrink: 0;
  min-width: 75px;
}

.log-message {
  flex: 1;
  color: #e2e8f0;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-all;
}

.log-item.log-success {
  border-left: 3px solid #22c55e;
}

.log-item.log-warning {
  border-left: 3px solid #f59e0b;
}

.log-item.log-error {
  border-left: 3px solid #ef4444;
}

.log-item.log-info {
  border-left: 3px solid #3b82f6;
}

.empty-log {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 180px;
  color: #64748b;
}

:deep(.el-empty__description) {
  color: #64748b;
}

.log-footer {
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.5);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.footer-btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.footer-btn:hover {
  transform: translateY(-1px);
}

.footer-btn.primary {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border: none;
  color: #fff;
}

.log-item-enter-active,
.log-item-leave-active {
  transition: all 0.3s ease;
}

.log-item-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}

.log-item-leave-to {
  opacity: 0;
  transform: translateX(10px);
}
</style>
