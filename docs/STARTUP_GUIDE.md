# DataLens 项目启动指南

## 🚀 项目已成功启动

### 服务状态

| 服务 | 地址 | 状态 |
|------|------|------|
| **后端 API** | http://localhost:8000 | ✅ 运行中 |
| **API 文档** | http://localhost:8000/docs | ✅ 可访问 |
| **前端应用** | http://localhost:5173 | ✅ 运行中 |
| **数据库** | 127.0.0.1:3306 | ✅ 已连接 |

### 快速访问

- **前端应用**：打开浏览器访问 http://localhost:5173
- **API 文档**：http://localhost:8000/docs (Swagger UI)
- **后端 API**：http://localhost:8000

### 项目架构

```
┌─────────────────────────────────────────────────────────┐
│                   前端 (Vue 3 + Vite)                    │
│              http://localhost:5173                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│              后端 API (FastAPI)                          │
│              http://localhost:8000                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Agent 层 (使用 MCP Client)                      │  │
│  │  NL2SQLAgent - 自然语言转 SQL                    │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ stdio transport
┌────────────────────▼────────────────────────────────────┐
│         MCP Server (独立进程)                            │
│  - 连接池管理                                            │
│  - 5 个数据库工具                                        │
│  - Schema 缓存                                           │
└────────────────────┬────────────────────────────────────┘
                     │ MySQL 连接
                ┌────▼─────┐
                │ MySQL DB │
                └──────────┘
```

### 配置信息

**数据库配置** (`config.json`)：
- **ecommerce** (当前)：127.0.0.1:3306
- **modelPlatform**：localhost:3306

**LLM 配置**：
- Provider：OpenAI-Compatible (阿里云通义千问)
- Model：glm-5
- Base URL：https://dashscope.aliyuncs.com/compatible-mode/v1

**MCP 配置**：
- 状态：✅ 已启用 (`use_mcp: true`)
- 连接池大小：5
- Schema 缓存 TTL：5 分钟

### 可用的 API 端点

#### 数据库管理
- `GET /api/databases` - 获取数据库列表
- `POST /api/databases` - 添加数据库
- `DELETE /api/databases/{name}` - 删除数据库
- `POST /api/databases/{name}/test` - 测试连接

#### 聊天/查询
- `POST /api/chat` - 发送自然语言查询
- `GET /api/conversations` - 获取对话历史
- `GET /api/conversations/{id}` - 获取特定对话

#### 配置
- `GET /api/config` - 获取配置
- `POST /api/config/model` - 更新模型配置

### 前端功能

- 💬 **聊天界面**：自然语言查询数据库
- 📊 **SQL 显示**：查看生成的 SQL 语句
- 📈 **结果展示**：表格形式显示查询结果
- ⚙️ **设置面板**：配置数据库和模型
- 📝 **对话历史**：保存和查看历史对话

### 开发工具

#### 后端开发
```bash
# 启动 API 服务器（已运行）
uvicorn api.main:app --reload

# 运行测试
python tests/test_mcp_refactoring.py

# CLI 模式
python main.py
```

#### 前端开发
```bash
# 启动开发服务器（已运行）
cd frontend && npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 日志文件

- **后端日志**：控制台输出
- **MCP 服务器日志**：`mcp_server.log`
- **前端日志**：浏览器控制台 (F12)

### 故障排查

#### 前端无法连接到后端
1. 检查后端是否运行：`curl http://localhost:8000`
2. 检查 CORS 配置（已启用）
3. 检查防火墙设置

#### MCP Server 错误
1. 检查数据库连接：`python -c "import mysql.connector; mysql.connector.connect(...)"`
2. 查看 `mcp_server.log` 日志
3. 重启后端服务

#### 前端加载缓慢
1. 清除浏览器缓存
2. 检查网络连接
3. 查看浏览器控制台错误

### 下一步

1. **测试功能**
   - 在前端输入自然语言查询
   - 查看生成的 SQL 和结果

2. **配置优化**
   - 调整 LLM 参数（temperature, max_tokens）
   - 添加更多数据库

3. **生产部署**
   - 构建前端：`npm run build`
   - 配置反向代理（Nginx）
   - 部署到服务器

### 技术栈

**后端**：
- Python 3.13
- FastAPI 0.135.3
- SQLAlchemy
- MySQL Connector 9.6.0
- MCP 1.27.0
- Anthropic SDK 0.94.1

**前端**：
- Vue 3.4.0
- Vite 5.0.0
- TypeScript 5.3.0
- Naive UI 2.38.0
- Pinia 2.1.0
- Axios 1.6.0

### 支持

- 📖 查看 [MCP_REFACTORING.md](MCP_REFACTORING.md) 了解 MCP 架构
- 📚 查看 [README.md](README.md) 了解项目概述
- 🏗️ 查看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解系统架构

---

**启动时间**：2026-04-15 19:00+
**状态**：✅ 全部就绪