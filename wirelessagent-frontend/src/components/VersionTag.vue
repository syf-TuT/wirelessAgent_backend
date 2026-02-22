<template>
  <div class="version-tag">
    <el-icon class="tag-icon">
      <info-filled />
    </el-icon>
    <span class="tag-text">无知识库版本</span>
    <div class="tag-shine"></div>
  </div>
</template>

<script setup lang="ts">
import { InfoFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.version-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%) !important;
  background-color: transparent !important;
  border: 2px solid rgba(255, 255, 255, 0.4) !important;
  color: #ffffff !important;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5px;
  backdrop-filter: blur(12px);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  cursor: default;
  z-index: 10;
}

.version-tag:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0.25) 100%) !important;
  background-color: transparent !important;
  border-color: rgba(255, 255, 255, 0.6) !important;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.tag-icon {
  font-size: 16px;
  animation: iconBounce 2s ease-in-out infinite;
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.tag-text {
  position: relative;
  z-index: 2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.tag-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
  z-index: 1;
}

.version-tag:hover .tag-shine {
  left: 100%;
}

@keyframes iconBounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}
</style>
