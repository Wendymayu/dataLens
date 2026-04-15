# Quick Start Guide - DataLens

## 5 Minutes Setup

### Step 1: Install Dependencies
```bash
cd datalens
pip install -r requirements.txt
```

### Step 2: Set Up API Key
Get an API key from your chosen provider:
- **Anthropic Claude**: https://console.anthropic.com/
- **OpenAI-Compatible** (推荐国内用户): 支持阿里云、智谱等
- **Alibaba Qwen**: https://dashscope.console.aliyun.com/
- **Zhipu GLM**: https://open.bigmodel.cn/

### Step 3: Choose Configuration Method

#### Method A: Use Config Template (推荐)
```bash
# OpenAI兼容API（国内推荐）
cp docs/examples/config/openai-compatible.json config.json

# Anthropic Claude
cp docs/examples/config/anthropic.json config.json

# 编辑config.json，填入真实的API Key和数据库信息
```

OpenAI兼容配置示例：
```json
{
  "model": {
    "provider": "openai-compatible",
    "model_name": "glm-5",
    "api_key": "你的API Key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "databases": {
    "ecommerce": {
      "name": "ecommerce",
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "你的数据库密码",
      "database": "ecommerce"
    }
  },
  "current_database": "ecommerce"
}
```

#### Method B: Interactive Setup
```bash
python main.py
```

The program will prompt you:
```
Choose provider (1-4): 4
Model name: glm-5
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
API Key: 你的API Key
```

### Step 4: Create Test Database (Optional)
```bash
# 创建电商测试数据库
mysql -h localhost -u root -p < ecommerce_schema.sql

# 可选：生成大量测试数据
python scripts/generate_test_data.py --users 500 --products 500 --orders 10000
```

## Basic Usage

Once configured, simply ask questions:

```
(mydb)> How many users are registered?
Response: Based on the database, there are 1,245 registered users.

(mydb)> Show me the top 5 products by sales
Response: Here are the top 5 products...

(mydb)> List orders from last month that haven't been shipped
Response: There are 23 unshipped orders from last month...
```

## Common Commands

| Command | Example | Description |
|---------|---------|-------------|
| Direct Query | `How many users?` | Ask any question about the database |
| Switch DB | `switch analytics` | Switch to a different database |
| List Databases | `config list` | Show all configured databases |
| Add Database | `config add` | Add new database connection |
| Configure Model | `config model` | Update or change LLM provider |
| Help | `help` | Show all commands |
| Exit | `exit` or `quit` | Exit the program |

## Configuration File

After first run, a `config.json` is created. You can manually edit it:

**Anthropic Claude配置**:
```json
{
  "model": {
    "provider": "anthropic",
    "model_name": "claude-3-5-sonnet-20241022",
    "api_key": "sk-ant-...",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  ...
}
```

**OpenAI兼容API配置** (推荐国内用户):
```json
{
  "model": {
    "provider": "openai-compatible",
    "model_name": "glm-5",
    "api_key": "sk-...",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  ...
}
```

**Important**: Don't commit `config.json` to version control (see `.gitignore`)!

## Troubleshooting

### "Database connection failed"
- Verify MySQL is running
- Check host, port, username, password
- Ensure the database exists

### "API Key Error"
- Double-check your API key
- Verify the provider is correct
- Check API key permissions

### "Unknown command"
- Use `help` to see available commands
- Type questions directly without prefixes

## Environment Variables (Alternative)

Instead of interactive setup, you can use environment variables:

```bash
export MODEL_PROVIDER=anthropic
export MODEL_NAME=claude-3-5-sonnet-20241022
export API_KEY=sk-ant-xxx

python main.py
```

## Example Queries by Database Type

### E-commerce Database
```
(shop)> How many orders were placed today?
(shop)> Which customers spent the most in Q4?
(shop)> What's the average product price by category?
```

### Analytics Database
```
(analytics)> Show me daily active users for the last week
(analytics)> Which features have the highest usage?
(analytics)> What's the bounce rate by page?
```

### CRM Database
```
(crm)> List all high-value customers
(crm)> How many open deals are there?
(crm)> Which sales reps have the best conversion rate?
```

## Full Documentation

- See [README.md](README.md) for complete feature list
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for project structure
- See [docs/examples/](docs/examples/) for configuration examples
- See [tests/README.md](tests/README.md) for test data generation

## Support for Multiple Models

The agent supports intelligent switching between providers. To compare:

```
(mydb)> config model
# Select provider 1 (Anthropic) - Most reliable SQL generation
# Select provider 2 (Qwen) - Faster, better for Chinese
# Select provider 3 (Zhipu) - Excellent reasoning capability
# Select provider 4 (OpenAI-Compatible) - Custom endpoints, flexible
```

推荐选择：
- **海外用户**: Anthropic Claude (效果最佳)
- **国内用户**: OpenAI-Compatible + 阿里云通义千问或智谱GLM (速度快)
- **中文查询**: Qwen 或 Zhipu (中文理解好)

## Next Steps

1. ✅ Successfully installed and configured
2. 📝 Ask your first database question
3. 🔄 Try switching between databases
4. 🛠️ Add more database connections as needed
5. 📚 Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system

---

**Need help?** Check the full [README.md](README.md) or review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details.
