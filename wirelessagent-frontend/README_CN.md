# 5G网络切片资源分配系统 - 前端界面

这是一个为无线智能体（WirelessAgent）创建的Vue.js前端界面，用于5G网络切片资源分配系统的可视化操作。

## 功能特性

- **文件上传**: 支持拖拽上传CSV格式的用户数据文件
- **实时日志**: 显示处理过程中的详细日志信息
- **结果展示**: 以表格和统计图表形式展示分配结果
- **数据导出**: 支持导出处理结果和日志文件
- **响应式设计**: 适配不同屏幕尺寸

## 技术栈

- **前端框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **构建工具**: Vite
- **HTTP客户端**: Axios
- **后端API**: FastAPI + Python

## 项目结构

```
wirelessagent-frontend/
├── src/
│   ├── components/          # Vue组件
│   │   ├── FileUpload.vue      # 文件上传组件
│   │   ├── ProcessLog.vue      # 处理日志组件
│   │   └── ResultsDisplay.vue  # 结果展示组件
│   ├── services/            # API服务
│   │   └── api.ts             # 后端API调用
│   ├── App.vue              # 主应用组件
│   └── main.ts             # 应用入口
├── public/                 # 静态资源
├── index.html             # HTML模板
├── package.json           # 项目依赖
└── vite.config.ts        # Vite配置
```

## 安装和运行

### 前端安装

```bash
cd wirelessagent-frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 运行

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 后端API服务器

### 启动后端服务器

```bash
cd F:\code\wirelessAgent_backend
python api_server.py
```

后端API将在 `http://localhost:8000` 运行

### API端点

- `POST /upload-csv` - 上传CSV文件
- `POST /process-csv` - 处理CSV文件并执行网络切片分配
- `GET /results` - 获取处理结果

## CSV文件格式

CSV文件应包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| RX_ID | 用户ID | 1 |
| X | X坐标 | 75.64 |
| Y | Y坐标 | 182.46 |
| Z | Z坐标 | 1.50 |
| SNR_dB | 信噪比(dB) | 6.23 |
| RX_Power_dBm | 接收功率(dBm) | -86.76 |
| CQI | 信道质量指示器(1-15) | 7 |
| LOS | 视距标志 | 0 |
| User_Request | 用户请求文本 | I need to stream 4K video |
| Request_Label | 请求标签(可选) | eMBB |

## 使用说明

1. **启动后端服务器**
   ```bash
   python api_server.py
   ```

2. **启动前端应用**
   ```bash
   cd wirelessagent-frontend
   npm run dev
   ```

3. **打开浏览器**
   访问 `http://localhost:5173`

4. **上传CSV文件**
   - 拖拽CSV文件到上传区域
   - 或点击上传区域选择文件

5. **开始处理**
   - 点击"开始处理"按钮
   - 查看处理日志
   - 等待处理完成

6. **查看结果**
   - 在"详细数据"标签页查看每个用户的分配结果
   - 在"统计概览"标签页查看统计数据

7. **导出结果**
   - 点击"导出结果"按钮下载CSV文件

## 界面设计

界面采用现代化的渐变设计风格：

- **主色调**: 紫色渐变 (#667eea → #764ba2)
- **卡片设计**: 半透明毛玻璃效果
- **动画效果**: 流畅的过渡动画
- **响应式布局**: 适配桌面和移动设备

## 组件说明

### FileUpload.vue
- 支持拖拽上传
- 显示文件信息
- 文件格式验证

### ProcessLog.vue
- 实时显示处理日志
- 不同类型日志使用不同颜色标识
- 支持日志导出

### ResultsDisplay.vue
- 表格展示详细分配结果
- 统计卡片显示关键指标
- 支持结果导出

## 注意事项

1. 确保后端API服务器正在运行
2. CSV文件格式必须符合要求
3. 处理大量用户数据可能需要较长时间
4. 建议使用Chrome或Edge浏览器以获得最佳体验

## 故障排除

### 前端无法连接后端
- 检查后端服务器是否运行
- 确认API地址配置正确 (http://localhost:8000)
- 检查防火墙设置

### 文件上传失败
- 确认CSV文件格式正确
- 检查文件大小是否过大
- 查看浏览器控制台错误信息

### 处理速度慢
- 减少CSV文件中的用户数量
- 检查系统资源使用情况
- 关闭其他占用资源的程序

## 开发说明

### 添加新功能

1. 在 `src/components/` 创建新组件
2. 在 `App.vue` 中引入和使用组件
3. 在 `src/services/api.ts` 中添加API调用方法

### 修改样式

- 全局样式在 `App.vue` 的 `<style>` 部分
- 组件样式在各自Vue文件的 `<style scoped>` 部分

### 调试

- 使用浏览器开发者工具查看网络请求
- 查看控制台日志和错误信息
- 使用Vue DevTools进行组件调试

## 许可证

本项目遵循原项目的许可证。
