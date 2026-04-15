# DataLens 项目结构说明

## 目录结构

```
datalens/
├── agent/                    # 核心代理模块
│   ├── __init__.py
│   ├── agent.py             # NL2SQL代理核心逻辑（多模型支持）
│   ├── cli.py               # 命令行界面（Rich库）
│   ├── config.py            # 配置管理（Pydantic模型）
│   ├── database.py          # MySQL数据库连接和操作
│   └── utils.py             # 工具函数
│
├── tests/                    # 测试数据和测试用例
│   ├── data/                # 生成的测试数据（JSON格式）
│   │   └── data_summary_*.json  # 数据生成摘要
│   ├── fixtures/            # 测试固件
│   ├── __init__.py
│   ├── test_example.py      # 示例测试
│   └ README.md              # 测试数据使用文档
│
├── scripts/                  # 脚本工具
│   ├── generate_test_data.py  # 测试数据生成脚本
│   └── clear_data.sql         # 清空数据库脚本
│
├── docs/                     # 文档
│   └ examples/              # 配置和使用示例
│     ├── config/            # 各LLM提供商的配置示例
│     │   ├── anthropic.json
│     │   ├── openai-compatible.json
│     │   ├── qwen.json
│     │   └ zhipu.json
│     └ README.md            # 配置指南
│
├── main.py                   # 程序入口
├── config.json              # 当前配置（不在git中）
├── config.example.json      # 配置示例模板
├── ecommerce_schema.sql     # 电商数据库建表脚本
├── requirements.txt         # Python依赖
├── .gitignore               # Git忽略规则
├── README.md                # 项目说明
├── ARCHITECTURE.md          # 架构文档
├── QUICKSTART.md            # 快速开始指南
└── PROJECT_SUMMARY.md       # 项目总结
```

## 核心模块说明

### agent/ - 核心代理模块

#### agent.py
- **功能**: NL2SQL转换的核心引擎
- **支持的模型**:
  - Anthropic Claude (Tool Use框架)
  - OpenAI-compatible (支持自定义URL)
  - Qwen (阿里通义千问)
  - Zhipu GLM (智谱AI)
- **主要方法**:
  - `query(user_query)`: 处理用户自然语言查询
  - `_extract_sql(text)`: 从响应中提取SQL语句

#### cli.py
- **功能**: 命令行交互界面
- **使用**: Rich库实现美化的终端输出
- **主要功能**:
  - 配置管理（config add/list/remove/model）
  - 数据库切换（switch）
  - 结果展示（表格、面板）

#### config.py
- **功能**: 配置文件管理
- **使用**: Pydantic模型进行配置验证
- **配置类**:
  - `ModelConfig`: 模型配置（provider, model_name, api_key, base_url）
  - `DatabaseConfig`: 数据库配置
  - `AppConfig`: 应用总配置
  - `ConfigManager`: 配置管理器

#### database.py
- **功能**: MySQL数据库操作
- **主要方法**:
  - `connect()`: 建立连接
  - `execute_query(sql)`: 执行SQL查询
  - `get_schema()`: 获取数据库结构
  - `disconnect()`: 关闭连接

### tests/ - 测试模块

#### data/
- 存放生成的测试数据摘要
- 包含用户、商品、订单的样本数据
- 文件命名格式: `data_summary_YYYYMMDD_HHMMSS.json`

#### fixtures/
- 测试固件和固定数据
- 用于单元测试的小规模数据

#### scripts/ - 工具脚本

#### generate_test_data.py
- **功能**: 生成大规模测试数据
- **参数**: 
  - `--users`: 用户数量（默认500）
  - `--products`: 商品数量（默认500）
  - `--orders`: 订单数量（默认10000）
- **输出**: 
  - 数据插入到数据库
  - 数据摘要保存到JSON文件

#### clear_data.sql
- 清空数据库所有数据（保留表结构）

### docs/examples/ - 配置示例

#### config/
- 各LLM提供商的完整配置示例
- 复制到根目录重命名为`config.json`即可使用

#### README.md
- 详细的配置指南
- 各提供商的特点和获取API Key的方法
- 多数据库配置示例

## 配置文件说明

### config.json (当前配置)

**位置**: 项目根目录  
**作用**: 存储当前使用的配置  
**格式**: JSON格式  
**安全**: 不提交到git（包含敏感信息）

```json
{
  "model": {
    "provider": "openai-compatible",
    "model_name": "glm-5",
    "api_key": "sk-xxxxxx",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "databases": {
    "ecommerce": {
      "name": "ecommerce",
      "host": "127.0.0.1",
      "port": 3306,
      "user": "root",
      "password": "52wendyma",
      "database": "ecommerce"
    }
  },
  "current_database": "ecommerce"
}
```

### config.example.json (配置模板)

**位置**: 项目根目录  
**作用**: 提供配置示例模板  
**提交**: 会提交到git（不含真实敏感信息）

## 数据库说明

### ecommerce_schema.sql

**作用**: 创建电商测试数据库  
**包含**:
- 建库语句
- 5个核心表的建表语句（users, categories, products, orders, order_items）
- 基础测试数据（10用户，20商品，14订单）
- 性能优化索引

## 依赖说明

### requirements.txt

核心依赖：
- `anthropic`: Anthropic Claude API客户端
- `openai`: OpenAI API客户端（用于兼容接口）
- `pymysql`: MySQL数据库连接
- `pydantic`: 配置验证
- `rich`: 命令行美化
- `faker`: 测试数据生成

## 使用流程

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置模型和数据库**
   ```bash
   python main.py
   # 或复制配置示例
   cp docs/examples/config/openai-compatible.json config.json
   # 编辑config.json填入真实的API Key和数据库信息
   ```

3. **创建测试数据库**（可选）
   ```bash
   mysql -h localhost -u root -p < ecommerce_schema.sql
   ```

4. **生成大量测试数据**（可选）
   ```bash
   python scripts/generate_test_data.py --users 500 --products 500 --orders 10000
   ```

5. **运行程序**
   ```bash
   python main.py
   ```

6. **查询数据库**
   ```
   (ecommerce)> 有多少个VIP会员？
   (ecommerce)> 销量最高的10个商品是什么？
   (ecommerce)> 本月订单总额是多少？
   ```

## 开发指南

### 添加新的LLM提供商

1. 在 `agent/config.py` 的 `ModelConfig` 中添加新provider
2. 在 `agent/agent.py` 中实现 `_call_newprovider()` 方法
3. 在 `agent/cli.py` 的 `config_model()` 中添加选择项
4. 在 `docs/examples/config/` 中添加配置示例

### 添加新的数据库支持

1. 在 `agent/database.py` 中扩展数据库连接逻辑
2. 添加新的数据库类型配置
3. 更新文档和示例

## 安全注意事项

- **config.json 不提交到git**: 已在.gitignore中配置
- **API Key 保护**: 使用环境变量或配置文件
- **数据库权限**: 建议使用只读权限的数据库用户
- **测试数据**: 生成的数据摘要文件不提交到git

## 文件清单

| 文件/目录 | 用途 | 是否提交git |
|-----------|------|-------------|
| agent/ | 核心代码 | ✓ |
| tests/fixtures/ | 测试固件 | ✓ |
| tests/data/*.json | 测试数据 | ✗ |
| scripts/ | 工具脚本 | ✓ |
| docs/ | 文档 | ✓ |
| main.py | 入口程序 | ✓ |
| config.json | 当前配置 | ✗ |
| config.example.json | 配置模板 | ✓ |
| ecommerce_schema.sql | 数据库脚本 | ✓ |
| requirements.txt | 依赖列表 | ✓ |
| README.md | 项目说明 | ✓ |
| .gitignore | Git忽略规则 | ✓ |

## 快速命令参考

```bash
# 安装
pip install -r requirements.txt

# 运行
python main.py

# 创建数据库
mysql -h localhost -u root -p < ecommerce_schema.sql

# 生成测试数据
python scripts/generate_test_data.py

# 清空数据
mysql -h localhost -u root -p ecommerce < scripts/clear_data.sql

# 测试配置
python tests/test_openai_compatible.py
```