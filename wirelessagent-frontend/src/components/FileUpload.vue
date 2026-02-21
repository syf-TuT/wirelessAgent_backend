<template>
  <div class="upload-container">
    <el-upload ref="uploadRef" class="upload-area" drag :auto-upload="false" :on-change="handleFileChange" :limit="1"
      accept=".csv" :file-list="fileList">
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽CSV文件到此处或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持格式：.csv，文件应包含用户请求和CQI信息
        </div>
      </template>
    </el-upload>

    <div v-if="selectedFile" class="file-info">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
      </el-descriptions>
    </div>

    <div v-if="selectedFile" class="action-buttons">
      <el-button type="primary" size="large" :loading="processing" @click="handleProcess" class="process-btn">
        <el-icon><video-play /></el-icon>
        开始处理
      </el-button>
      <el-button size="large" @click="handleClear" class="clear-btn">
        <el-icon>
          <delete />
        </el-icon>
        清除文件
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, VideoPlay, Delete } from '@element-plus/icons-vue'
import type { UploadFile, UploadUserFile } from 'element-plus'

const emit = defineEmits<{
  process: [file: File]
  clear: []
}>()

const uploadRef = ref()
const fileList = ref<UploadUserFile[]>([])
const selectedFile = ref<File | null>(null)
const processing = ref(false)

const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

const handleProcess = () => {
  if (selectedFile.value) {
    processing.value = true
    emit('process', selectedFile.value)
  }
}

const handleClear = () => {
  fileList.value = []
  selectedFile.value = null
  processing.value = false
  emit('clear')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

defineExpose({
  setProcessing: (value: boolean) => {
    processing.value = value
  }
})
</script>

<style scoped>
.upload-container {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.upload-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

:deep(.el-upload) {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
}

:deep(.el-upload-list) {
  display: none;
}

:deep(.el-upload-dragger) {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 48px 32px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
  border: 2px dashed rgba(99, 102, 241, 0.4);
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 180px;
  width: 100%;
  position: relative;
  cursor: pointer;
}

:deep(.el-upload-dragger:hover) {
  border-color: rgba(99, 102, 241, 0.8);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(168, 85, 247, 0.25) 100%);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.25);
}

:deep(.el-upload-dragger.is-dragover) {
  border-color: rgba(99, 102, 241, 1);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.35) 0%, rgba(168, 85, 247, 0.35) 100%);
  transform: scale(1.02);
}

:deep(.el-icon--upload) {
  font-size: 64px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3));
  transition: all 0.3s ease;
}

:deep(.el-upload-dragger:hover .el-icon--upload) {
  transform: scale(1.1);
  filter: drop-shadow(0 6px 16px rgba(99, 102, 241, 0.4));
}

:deep(.el-upload__text) {
  color: #e2e8f0;
  font-size: 16px;
  font-weight: 500;
  line-height: 1.6;
}

:deep(.el-upload__text em) {
  color: #a78bfa;
  font-style: normal;
  font-weight: 700;
  text-decoration: underline;
  text-decoration-color: rgba(167, 139, 250, 0.5);
  text-underline-offset: 4px;
}

:deep(.el-upload__tip) {
  color: #64748b;
  font-size: 13px;
  margin-top: 16px;
  padding: 0 20px;
  text-align: center;
}

.file-info {
  margin-top: 20px;
  background: rgba(30, 41, 59, 0.7);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

:deep(.el-descriptions) {
  --el-text-color-regular: #cbd5e1;
  --el-descriptions-border-color: rgba(255, 255, 255, 0.08);
  --el-descriptions-table-border-color: rgba(255, 255, 255, 0.08);
  --el-fill-color-light: rgba(15, 23, 42, 0.4);
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #94a3b8;
}

:deep(.el-descriptions__body .el-descriptions__table .el-descriptions__cell.is-bordered-label) {
  background: rgba(15, 23, 42, 0.6);
}

:deep(.el-descriptions__content) {
  color: #e2e8f0;
  font-weight: 500;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.process-btn,
.clear-btn {
  min-width: 140px;
  font-weight: 600;
  border-radius: 10px;
  padding: 12px 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.process-btn {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border: none;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.process-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.process-btn:active {
  transform: translateY(0);
}

.clear-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.clear-btn:active {
  transform: translateY(0);
}
</style>
