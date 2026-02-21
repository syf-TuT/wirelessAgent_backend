<template>
  <div class="app-container">
    <div class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <el-icon class="logo-icon"><connection /></el-icon>
          <h1 class="app-title">5G网络切片资源分配系统</h1>
        </div>
        <div class="header-info">
          <el-tag type="info" effect="plain">无知识库版本</el-tag>
        </div>
      </div>
    </div>

    <div class="app-main">
      <el-row :gutter="20" class="top-row">
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <div class="panel-container">
            <FileUpload
              ref="fileUploadRef"
              @process="handleFileProcess"
              @clear="handleFileClear"
            />
          </div>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <div class="panel-container">
            <ProcessLog :logs="logs" @clear="clearLogs" />
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="bottom-row">
        <el-col :span="24">
          <div class="panel-container results-panel">
            <ResultsDisplay
              :results="results"
              @export="exportResults"
              @clear="clearResults"
            />
          </div>
        </el-col>
      </el-row>
    </div>

    <div v-if="processing" class="processing-overlay">
      <div class="processing-content">
        <el-progress type="circle" :percentage="uploadProgress" :width="120" />
        <h3>正在处理中...</h3>
        <p>{{ uploadProgress }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import FileUpload from './components/FileUpload.vue'
import ProcessLog from './components/ProcessLog.vue'
import ResultsDisplay from './components/ResultsDisplay.vue'
import apiService from './services/api'

interface LogEntry {
  type: 'info' | 'success' | 'warning' | 'error'
  message: string
  time: string
}

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

const fileUploadRef = ref()
const logs = ref<LogEntry[]>([])
const results = ref<AllocationResult[]>([])
const processing = ref(false)
const uploadProgress = ref(0)

const addLog = (type: 'info' | 'success' | 'warning' | 'error', message: string) => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.push({ type, message, time })
}

const handleFileProcess = async (file: File) => {
  try {
    processing.value = true
    uploadProgress.value = 0
    addLog('info', `开始处理文件: ${file.name}`)
    addLog('info', `文件大小: ${(file.size / 1024).toFixed(2)} KB`)

    const response = await apiService.processCSV(file, (progress) => {
      uploadProgress.value = progress
      if (progress % 20 === 0) {
        addLog('info', `上传进度: ${progress}%`)
      }
    })

    addLog('success', '文件上传成功')
    addLog('info', '开始解析CSV文件...')

    await new Promise(resolve => setTimeout(resolve, 500))
    addLog('success', 'CSV文件解析成功')

    if (response && response.results) {
      results.value = response.results
      addLog('success', `成功解析 ${response.results.length} 条用户记录`)
      addLog('info', '开始网络切片资源分配...')

      await new Promise(resolve => setTimeout(resolve, 1000))

      for (let i = 0; i < response.results.length; i++) {
        const result = response.results[i]
        const progress = Math.round(((i + 1) / response.results.length) * 100)
        uploadProgress.value = progress

        addLog('info', `正在处理用户 ${result.user_id}: ${result.request.substring(0, 50)}...`)

        await new Promise(resolve => setTimeout(resolve, 300))

        if (result.allocation_failed) {
          addLog('error', `用户 ${result.user_id} 分配失败: ${result.slice_type}`)
        } else {
          addLog('success', `用户 ${result.user_id} 分配成功: ${result.slice_type} 切片, 带宽 ${result.bandwidth} MHz, 速率 ${result.rate} Mbps`)
        }
      }

      addLog('success', '所有用户处理完成')
      addLog('info', `成功分配: ${results.value.filter(r => !r.allocation_failed).length} 条`)
      addLog('info', `分配失败: ${results.value.filter(r => r.allocation_failed).length} 条`)

      ElMessage.success('处理完成！')
    } else {
      addLog('warning', '未收到有效结果数据')
    }
  } catch (error: any) {
    console.error('Process error:', error)
    addLog('error', `处理失败: ${error.message || '未知错误'}`)
    ElMessage.error('处理失败，请检查文件格式')
  } finally {
    processing.value = false
    uploadProgress.value = 0
    if (fileUploadRef.value) {
      fileUploadRef.value.setProcessing(false)
    }
  }
}

const handleFileClear = () => {
  addLog('info', '已清除上传文件')
}

const clearLogs = () => {
  logs.value = []
  addLog('info', '日志已清空')
}

const clearResults = () => {
  results.value = []
  addLog('info', '结果已清空')
}

const exportResults = () => {
  addLog('success', '结果已导出')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 18px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-icon {
  font-size: 32px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.4));
}

.app-title {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

.header-info {
  display: flex;
  gap: 12px;
}

.app-main {
  flex: 1;
  padding: 28px 32px;
  max-width: 1800px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.top-row {
  flex-shrink: 0;
}

.bottom-row {
  flex: 1;
  min-height: 0;
}

.panel-container {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(16px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  padding: 20px;
  display: flex;
  flex-direction: column;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.top-row .panel-container {
  height: 420px;
  min-height: 420px;
}

.results-panel {
  height: calc(100vh - 540px);
  min-height: 520px;
}

.panel-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.15);
}

.processing-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.processing-content {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 56px 64px;
  border-radius: 24px;
  text-align: center;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
  animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes scaleIn {
  from {
    transform: scale(0.85);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.processing-content h3 {
  margin: 24px 0 12px;
  font-size: 20px;
  color: #e2e8f0;
  font-weight: 600;
}

.processing-content p {
  margin: 0;
  font-size: 16px;
  color: #94a3b8;
}

:deep(.el-progress__text) {
  font-size: 18px !important;
  font-weight: 700 !important;
  color: #6366f1 !important;
}

:deep(.el-progress-circle__track) {
  stroke: rgba(255, 255, 255, 0.08);
}

:deep(.el-progress-circle__path) {
  stroke: url(#gradient);
}

:deep(.el-progress-circle) {
  position: relative;
}

:deep(.el-progress-circle svg) {
  width: 100%;
  height: 100%;
}

@media (max-width: 1600px) {
  .app-main {
    padding: 24px 28px;
  }
}

@media (max-width: 1400px) {
  .app-main {
    padding: 20px 24px;
  }

  .top-row .panel-container {
    height: 380px;
    min-height: 380px;
  }

  .results-panel {
    height: calc(100vh - 500px);
    min-height: 480px;
  }
}

@media (max-width: 1200px) {
  .app-header {
    padding: 14px 20px;
  }

  .app-main {
    padding: 18px 20px;
    gap: 16px;
  }

  .app-title {
    font-size: 18px;
  }

  .top-row .panel-container {
    height: 360px;
    min-height: 360px;
  }

  .results-panel {
    height: calc(100vh - 460px);
    min-height: 440px;
  }
}

@media (max-width: 992px) {
  .app-main {
    gap: 14px;
  }

  .top-row .panel-container {
    height: 340px;
    min-height: 340px;
  }

  .results-panel {
    height: auto;
    min-height: 420px;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 12px 16px;
  }

  .app-main {
    padding: 14px 16px;
  }

  .app-title {
    font-size: 16px;
  }

  .logo-icon {
    font-size: 26px;
  }

  .top-row .panel-container {
    height: 320px;
    min-height: 320px;
  }

  .panel-container {
    padding: 16px;
  }
}
</style>
