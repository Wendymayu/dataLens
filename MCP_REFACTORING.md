# MCP 重构说明

## 概述

DataLens 已成功集成 MCP (Model Context Protocol) 架构，将数据库访问层抽取为独立的 MCP Server。

## 架构变更

### 之前
```
Agent → DatabaseManager → MySQL
```

### 之后
```
Agent → MCP Client → MCP Server → Connection Pool → MySQL
```

## 主要改进

1. **连接池管理**：使用 MySQL 连接池，提升性能和资源利用
2. **解耦架构**：数据库访问逻辑独立于 Agent
3. **统一接口**：标准化的 MCP 工具定义
4. **Schema 缓存**：5 分钟 TTL，支持手动刷新
5. **向后兼容**：保留 DatabaseManager，可通过配置切换

## 新增文件

```
mcp/
├── __init__.py
├── server.py                 # MCP Server 主程序
├── connection_pool.py        # 连接池管理
├── config.py                 # MCP 配置
└── tools/
    ├── __init__.py
    └── database_tools.py     # 数据库工具实现

agent/
└── mcp_client.py             # MCP Client 包装

api/services/
└── mcp_service.py            # MCP 服务管理
```

## MCP Tools

MCP Server 提供以下工具：

1. **execute_query** - 执行 SQL 查询（只读）
2. **get_schema** - 获取数据库结构
3. **get_table_sample** - 获取表样本数据
4. **refresh_schema** - 刷新 schema 缓存
5. **test_connection** - 测试数据库连接

## 配置

在 `config.json` 中添加：

```json
{
  "use_mcp": true
}
```

- `true`：使用 MCP 模式（默认，推荐）
- `false`：使用 legacy DatabaseManager 模式

## 使用方式

### CLI 模式

```bash
python main.py
```

自动根据 `config.json` 中的 `use_mcp` 配置选择模式。

### API 模式

```bash
uvicorn api.main:app --reload
```

FastAPI 启动时会自动初始化 MCP Service（如果启用）。

## 测试

运行测试验证 MCP 功能：

```bash
python tests/test_mcp_refactoring.py
```

测试内容：
- MCP 模式的 schema 获取
- Legacy 模式的 schema 获取
- 两种模式的对比

## 安装依赖

```bash
pip install -r requirements.txt
```

新增依赖：
- `mcp>=0.9.0`

## 迁移指南

### 从旧版本迁移

1. **安装新依赖**
   ```bash
   pip install mcp>=0.9.0
   ```

2. **更新配置**（可选）
   在 `config.json` 中添加 `"use_mcp": true`

3. **测试**
   ```bash
   python tests/test_mcp_refactoring.py
   ```

4. **如遇问题，回退到 legacy 模式**
   设置 `"use_mcp": false`

## 性能优势

- **连接复用**：连接池避免频繁创建/销毁连接
- **Schema 缓存**：减少重复的 schema 查询
- **并发支持**：连接池支持多个并发请求

## 故障排查

### MCP Server 启动失败

检查：
1. 数据库配置是否正确
2. 数据库是否可访问
3. 查看 `mcp_server.log` 日志

### 回退到 legacy 模式

在 `config.json` 中设置：
```json
{
  "use_mcp": false
}
```

## 后续扩展

- [ ] 支持 PostgreSQL
- [ ] 支持 SQLite
- [ ] 查询结果缓存
- [ ] SQL 优化建议
- [ ] 分布式 MCP Server（SSE transport）

## 技术细节

### 连接池配置

- 默认池大小：5 个连接
- 连接超时：自动重连
- Schema 缓存 TTL：300 秒（5 分钟）

### 安全性

- 只允许只读查询（SELECT, SHOW, DESCRIBE, EXPLAIN）
- 查询结果限制：最多 100 行
- SQL 注入防护：参数化查询

## 贡献

欢迎提交 Issue 和 Pull Request！
