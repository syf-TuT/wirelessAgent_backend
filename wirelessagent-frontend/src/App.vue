<template>
  <div class="app-container">
    <div class="app-header">
      <div class="header-background">
        <div class="grid-pattern"></div>
        <div class="gradient-overlay"></div>
        <div class="particles">
          <div class="particle" v-for="i in 20" :key="i" :style="getParticleStyle(i)"></div>
        </div>
      </div>
      <div class="header-content">
        <div class="logo-section">
          <div class="logo-wrapper">
            <el-icon class="logo-icon">
              <connection />
            </el-icon>
            <div class="logo-glow"></div>
          </div>
          <div class="title-group">
            <h1 class="app-title">5G网络切片资源分配系统</h1>
            <p class="app-subtitle">Network Slice Resource Allocation System</p>
          </div>
        </div>
        <div class="header-info">
          <VersionTag />
        </div>
      </div>
    </div>

    <div class="app-main">
      <el-row :gutter="20" class="top-row">
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <div class="panel-container">
            <FileUpload ref="fileUploadRef" @process="handleFileProcess" @clear="handleFileClear" />
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
            <ResultsDisplay :results="results" @export="exportResults" @clear="clearResults" />
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
import VersionTag from './components/VersionTag.vue'
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

const getParticleStyle = (index: number) => {
  const size = Math.random() * 4 + 2
  const left = Math.random() * 100
  const top = Math.random() * 100
  const delay = Math.random() * 5
  const duration = Math.random() * 3 + 2
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
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
  background: #ffffff;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.app-header {
  position: relative;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 20px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%);
  z-index: 0;
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(168, 85, 247, 0.3) 0%, transparent 50%);
  animation: gradientPulse 8s ease-in-out infinite;
}

@keyframes gradientPulse {

  0%,
  100% {
    opacity: 0.6;
  }

  50% {
    opacity: 1;
  }
}

.grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 30px 30px;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% {
    transform: translate(0, 0);
  }

  100% {
    transform: translate(30px, 30px);
  }
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: particleFloat linear infinite;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.8);
}

@keyframes particleFloat {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }

  10% {
    opacity: 1;
  }

  90% {
    opacity: 1;
  }

  100% {
    transform: translateY(-100vh) translateX(20px);
    opacity: 0;
  }
}

.header-content {
  max-width: 1800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  padding: 12px 20px;
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-section:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.25);
}

.logo-section:active {
  transform: translateY(-1px) scale(1.01);
}

.logo-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  font-size: 42px;
  background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.4));
  transition: all 0.4s ease;
  position: relative;
  z-index: 2;
}

.logo-glow {
  position: absolute;
  width: 60px;
  height: 60px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: glowPulse 3s ease-in-out infinite;
  z-index: 1;
}

@keyframes glowPulse {

  0%,
  100% {
    transform: scale(1);
    opacity: 0.5;
  }

  50% {
    transform: scale(1.3);
    opacity: 0.8;
  }
}

.logo-section:hover .logo-icon {
  transform: scale(1.15) rotate(5deg);
  filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.6));
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.app-title {
  font-size: 26px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.8px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  line-height: 1.2;
}

.app-subtitle {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.logo-section:hover .app-title {
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
  transform: translateX(3px);
}

.logo-section:hover .app-subtitle {
  color: rgba(255, 255, 255, 1);
  transform: translateX(3px);
}

.header-info {
  display: flex;
  gap: 20px;
  align-items: center;
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
  background: #ffffff;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
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
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: rgba(99, 102, 241, 0.2);
}

.processing-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
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
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 56px 64px;
  border-radius: 24px;
  text-align: center;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
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
  color: #1e293b;
  font-weight: 600;
}

.processing-content p {
  margin: 0;
  font-size: 16px;
  color: #64748b;
}

:deep(.el-progress__text) {
  font-size: 18px !important;
  font-weight: 700 !important;
  color: #6366f1 !important;
}

:deep(.el-progress-circle__track) {
  stroke: rgba(99, 102, 241, 0.1);
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

  .app-header {
    padding: 18px 28px;
  }

  .logo-section {
    padding: 10px 16px;
    gap: 16px;
  }

  .logo-icon {
    font-size: 38px;
  }

  .app-title {
    font-size: 24px;
  }

  .app-subtitle {
    font-size: 11px;
  }
}

@media (max-width: 1400px) {
  .app-main {
    padding: 20px 24px;
  }

  .app-header {
    padding: 16px 24px;
  }

  .logo-section {
    padding: 8px 14px;
    gap: 14px;
  }

  .logo-icon {
    font-size: 36px;
  }

  .app-title {
    font-size: 22px;
  }

  .app-subtitle {
    font-size: 10px;
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

  .logo-section {
    padding: 6px 12px;
    gap: 12px;
  }

  .logo-icon {
    font-size: 32px;
  }

  .app-title {
    font-size: 20px;
  }

  .app-subtitle {
    display: none;
  }

  .app-main {
    padding: 18px 20px;
    gap: 16px;
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

  .logo-section {
    padding: 8px 12px;
    gap: 10px;
  }

  .logo-icon {
    font-size: 28px;
  }

  .app-title {
    font-size: 18px;
  }

  .app-subtitle {
    display: none;
  }

  .header-info {
    gap: 8px;
  }

  .app-main {
    padding: 14px 16px;
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
