# DataLens - Intelligent Data Analysis Platform

An AI-powered data analysis platform that converts natural language questions into SQL queries, executes them against databases, and returns natural language responses. Supports multiple LLM providers (Anthropic Claude, Alibaba Qwen, Zhipu GLM, and OpenAI-compatible APIs).

## Features

✨ **Core Features**
- Convert natural language to SQL automatically
- Support for multiple LLM providers (Anthropic, Qwen, Zhipu, OpenAI-compatible)
- Interactive CLI interface with Rich formatting
- Multiple database configuration and switching
- Automatic schema detection and context awareness
- Real-time query execution and result analysis
- Custom API endpoint support (base_url configuration)

## Quick Start

### 1. Installation

```bash
cd datalens
pip install -r requirements.txt
```

### 2. Configuration

Run the agent and follow interactive setup:

```bash
python main.py
```

The program will prompt you to:
1. Configure an LLM model (choose provider and API key)
2. Add a MySQL database connection

### 3. Basic Usage

Once configured, you can simply ask questions in natural language:

```
(myapp)> How many users are there?
(myapp)> Show me the top 10 orders by price
(myapp)> List all products in category 'electronics'
```

## Configuration Guide

### Model Configuration (LLM Providers)

#### 1. Anthropic Claude (Recommended)
```
Provider: anthropic
Model: claude-3-5-sonnet-20241022 (or claude-opus-4, claude-sonnet-4)
API Key: Get from https://console.anthropic.com/
```

#### 2. OpenAI-Compatible API (支持自定义URL)
```
Provider: openai-compatible
Model: glm-5, qwen-max, 或其他模型名称
API Key: Your API key
Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1 (阿里云)
         或其他OpenAI兼容的API端点
```
支持的服务商：阿里云通义千问、智谱GLM、DeepSeek等所有OpenAI兼容API

#### 3. Alibaba Qwen (阿里通义千问)
```
Provider: qwen
Model: qwen-turbo (or qwen-plus, qwen-max)
API Key: Get from https://dashscope.console.aliyun.com/
```

#### 4. Zhipu AI GLM (智谱 AI)
```
Provider: zhipu
Model: glm-4 (or glm-3-turbo, glm-4v)
API Key: Get from https://open.bigmodel.cn/
```

### Database Configuration

The agent automatically creates a `config.json` file after first run:

```json
{
  "model": {
    "provider": "anthropic",
    "model_name": "claude-3-5-sonnet-20241022",
    "api_key": "your-api-key",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "databases": {
    "mydb": {
      "name": "mydb",
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "password",
      "database": "myapp_db"
    }
  },
  "current_database": "mydb"
}
```

OpenAI兼容API配置示例（支持自定义base_url）：
```json
{
  "model": {
    "provider": "openai-compatible",
    "model_name": "glm-5",
    "api_key": "your-api-key",
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
      "password": "password",
      "database": "ecommerce_db"
    }
  },
  "current_database": "ecommerce"
}
```

Or use the interactive CLI:
```
> config add      # Add new database
> config list     # List all databases
> config remove   # Remove a database
> config model    # Update LLM configuration
> switch <name>   # Switch active database
```

## Usage Examples

### Example 1: Simple Query
```
(shop)> How many products are in stock?
Response: Based on the database, there are 1,245 products currently in stock.
```

### Example 2: Complex Analysis
```
(shop)> Show me the top 5 customers by total spending in the last quarter
Response: Here are the top 5 customers by spending...
```

### Example 3: Data Filter
```
(shop)> Which orders were placed in March 2024 and are still pending?
Response: There are 34 pending orders from March 2024...
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `help` | Show all available commands |
| `config add` | Add a new database connection |
| `config list` | List all configured databases |
| `config remove` | Remove a database configuration |
| `config model` | Configure/update LLM model |
| `switch <db_name>` | Switch to a different database |
| `exit` / `quit` | Exit the program |
| Any text | Natural language query |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

### Key Components

```
datalens/
├── main.py              Entry point and interaction loop
├── agent/
│   ├── cli.py          Command-line interface (Rich)
│   ├── agent.py        NL2SQL Agent (Multi-model support)
│   ├── database.py     MySQL connection and query execution
│   ├── config.py       Configuration management
│   └── utils.py        Helper functions
├── tests/
│   ├── data/           Generated test data
│   ├── fixtures/       Test fixtures
│   └── README.md       Test data documentation
├── scripts/
│   ├── generate_test_data.py  Test data generator
│   └── clear_data.sql         Clear database script
├── docs/
│   └ examples/
│     ├── config/       Configuration examples for different providers
│     └ README.md       Configuration guide
├── config.json         Active configuration (not in git)
├── config.example.json Example configuration template
└ ecommerce_schema.sql Database schema script
└ README.md
└ ARCHITECTURE.md
```

## Supported Model Providers

| Provider | Models | Strengths |
|----------|--------|-----------|
| **Anthropic** | Claude 3.5 Sonnet, Opus, Haiku | Best SQL generation, strong reasoning |
| **OpenAI-Compatible** | Any OpenAI-compatible model | Flexible, supports custom endpoints |
| **Qwen** | Qwen Turbo, Plus, Max | Fast, low latency, good Chinese support |
| **Zhipu AI** | GLM-4, GLM-3-Turbo | Excellent for Chinese queries |

## Limitations & Future

### Current Limitations
- Only MySQL support (MySQL 5.7+)
- Limited to SELECT-like read queries (safe mode)
- Single database connection per session

### Future Extensions
- PostgreSQL, SQLite, SQL Server support
- Schema caching for performance
- Query result caching
- Multi-turn conversation context
- Query explanation and optimization suggestions

## Environment Variables

Optional: Set these to skip interactive configuration:

```bash
export MODEL_PROVIDER=anthropic
export MODEL_NAME=claude-3-5-sonnet-20241022
export API_KEY=your-api-key
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=password
export DB_NAME=myapp_db
```

## Troubleshooting

### API Key Error
- Verify your API key is correct for the chosen provider
- Check API key permissions and rate limits

### Database Connection Error
- Verify MySQL server is running
- Check hostname, port, and credentials
- Ensure the database name exists

### Query Execution Error
- Check database schema compatibility
- Verify user has SELECT permissions
- Review generated SQL in agent output

## Security Notes

⚠️ **Important**
- Store API keys securely (use environment variables or `.env` files)
- Never commit `config.json` with real credentials
- Use database user with minimal permissions (read-only recommended)
- Only connect to trusted networks/databases

## Contributing

Contributions welcome! Areas for enhancement:
- Support for additional database systems
- Performance optimizations
- Better error handling
- Additional LLM provider integration

## License

MIT License - See LICENSE file for details
