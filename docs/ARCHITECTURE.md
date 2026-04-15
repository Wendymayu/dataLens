# DataLens - Architecture Documentation

## 1. System Overview

The DataLens is a natural language to SQL conversion system that leverages Large Language Models (LLMs) to understand user intent, generate appropriate SQL queries, execute them against MySQL databases, and provide intelligent analysis of results.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                          │
│              (Rich Terminal UI)                           │
│  - User Input Processing                                 │
│  - Database Configuration Management                     │
│  - Result Display & Formatting                           │
└────────────────────┬────────────────────────────────────┘
                     │ user_query / command
                     │
┌────────────────────▼────────────────────────────────────┐
│            Agent Processing Layer                         │
│                  (agent.py)                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │  DataLens (Multi-Model Support)               │ │
│  │  - Anthropic Claude                               │ │
│  │  - Alibaba Qwen                                   │ │
│  │  - Zhipu GLM                                      │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Tool Use Framework                               │ │
│  │  - get_schema() - Retrieve database structure     │ │
│  │  - execute_query() - Execute SQL and get results  │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ SQL query / schema
                     │
    ┌────────────────┴──────────────────────┐
    │                                       │
┌───▼──────────┐                  ┌────────▼────────┐
│   MySQL DB   │                  │  LLM Provider   │
│              │                  │  (Claude/Qwen/  │
│ - Tables     │                  │   Zhipu)        │
│ - Data       │                  │                 │
│ - Schema     │                  │ API Endpoints   │
└──────────────┘                  └─────────────────┘
```

## 2. Component Architecture

### 2.1 Configuration Management (`config.py`)

**Purpose**: Handle all configuration aspects of the application.

**Key Classes**:
- `DatabaseConfig`: Pydantic model for database connection parameters
- `ModelConfig`: Configuration for LLM provider and settings
- `AppConfig`: Aggregates database and model configurations
- `ConfigManager`: Manages loading, saving, and updating configurations

**Responsibilities**:
- Load config from JSON file or environment variables
- Store database credentials securely
- Manage multiple database profiles
- Track current active database
- Provide CRUD operations for database configs

```python
# Example flow:
config = ConfigManager("config.json")
config.add_database("prod", DatabaseConfig(...))
config.set_current_database("prod")
db = config.get_database()  # Get current database config
```

**File Format** (config.json):
```json
{
  "model": {
    "provider": "anthropic",
    "model_name": "claude-3-5-sonnet-20241022",
    "api_key": "..."
  },
  "databases": {
    "mydb": {
      "name": "mydb",
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "...",
      "database": "myapp_db"
    }
  },
  "current_database": "mydb"
}
```

### 2.2 Database Module (`database.py`)

**Purpose**: Abstract database operations and provide a clean interface for querying.

**Key Class**:
- `DatabaseManager`: Handles MySQL connections and query execution

**Key Methods**:
- `connect()`: Establish connection to MySQL
- `execute_query(sql)`: Execute SQL and return results as list of dicts
- `get_schema()`: Retrieve complete database schema (table names and columns)
- `test_connection()`: Verify database connectivity

**Design Decisions**:
- Uses dictionary cursor for intuitive result access
- Returns data as plain dictionaries for easy LLM processing
- Implements proper error handling with meaningful messages
- Includes schema retrieval to support Agent context

```python
# Example usage:
db = DatabaseManager(db_config)
schema = db.get_schema()
results = db.execute_query("SELECT * FROM users LIMIT 10")
```

### 2.3 Agent Module (`agent.py`)

**Purpose**: Core NL2SQL conversion and execution engine.

**Key Class**:
- `NL2SQLAgent`: Orchestrates the natural language to SQL pipeline

**Architecture - Multi-Model Support**:

The agent supports three model providers with provider-specific implementations:

#### Anthropic Claude (Recommended)
- Uses **Tool Use** framework for reliable function calling
- Implements agent loop with max 10 iterations
- Tools: `execute_query(sql)`
- Best for SQL generation and reasoning

**Flow**:
1. User query + schema → send to Claude with tool definition
2. Claude generates SQL using tool_use block
3. Agent executes SQL and returns results
4. Claude analyzes results and generates final answer

```python
# Tool definition sent to Claude:
{
  "name": "execute_query",
  "description": "Execute SQL query and return results",
  "input_schema": {
    "type": "object",
    "properties": {
      "sql": {"type": "string"}
    }
  }
}
```

#### Alibaba Qwen (Dashscope)
- Direct prompt-based query generation
- Fast response times
- Good for Chinese language queries
- Uses `dashscope.Generation` API

#### Zhipu GLM
- Direct chat completion model
- Strong Chinese language capabilities
- Uses standard OpenAI-compatible interface
- Good for analytical queries

**Design Patterns**:

```python
# Provider abstraction:
class NL2SQLAgent:
    def _init_client(self):
        # Dynamically load appropriate client based on provider
        
    def query(self, user_query):
        provider = self.model_config.provider
        if provider == "anthropic":
            return self._call_anthropic(user_query)
        elif provider == "qwen":
            return self._call_qwen(user_query)
        # ... etc
```

### 2.4 CLI Interface (`cli.py`)

**Purpose**: Provide user-friendly command-line interaction.

**Key Class**:
- `CliInterface`: Manages all CLI interactions using Rich library

**Features**:
- Beautiful terminal formatting with Rich library
- Interactive command processing
- Color-coded status messages
- Table display for database listings
- Panel display for query results

**Key Methods**:
- `print_banner()`: Show welcome screen
- `config_add()`: Interactive database addition
- `config_list()`: Display databases in table
- `config_remove()`: Remove database
- `config_model()`: Configure LLM
- `switch_database(db_name)`: Change active database
- `display_query_result()`: Format and show results
- `display_error()`: Show error messages

**Rich Usage**:
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Creates formatted output like:
╔═══════════════════════════════════════╗
║     DataLens - Query Assistant    ║
╚═══════════════════════════════════════╝
```

### 2.5 Main Program (`main.py`)

**Purpose**: Application entry point and main interaction loop.

**Flow**:
```
1. Initialize ConfigManager
2. Initialize CliInterface
3. Check if model and database are configured
   - If not, prompt for configuration
4. Show banner
5. Enter main loop:
   - Read user input
   - Parse commands (config, switch, help, query)
   - Execute appropriate handlers
   - Process natural language queries through Agent
   - Display results
6. Cleanup and exit on user request
```

**Command Processing**:
```
User Input
    ↓
[Parse Input]
    ├─→ "exit/quit" → Exit program
    ├─→ "help" → Show help
    ├─→ "config *" → Handle config commands
    ├─→ "switch *" → Switch database
    └─→ Other → Process as NL query
```

### 2.6 Utilities (`utils.py`)

**Purpose**: Provide helper functions and utilities.

**Key Functions**:
- `get_logger(name)`: Get configured logger for module
- `serialize_result(data)`: Convert results to JSON string
- `truncate_text(text, max_length)`: Truncate long text

## 3. Data Flow Diagrams

### 3.1 Query Processing Flow

```
User Input
    ↓
┌───────────────────────────────────────┐
│  Parse User Query                     │
│  (CLI processes input)                │
└───────────────┬───────────────────────┘
                ↓
┌───────────────────────────────────────┐
│  Initialize NL2SQLAgent               │
│  - Load database config               │
│  - Retrieve database schema           │
│  - Initialize LLM client              │
└───────────────┬───────────────────────┘
                ↓
┌───────────────────────────────────────┐
│  Send to LLM with Tools               │
│  - User query                         │
│  - Database schema                    │
│  - Tool definitions                   │
└───────────────┬───────────────────────┘
                ↓
        ┌─────────────────┐
        │ LLM Processing  │
        │ (Agent loop)    │
        └────────┬────────┘
                 ↓
      ┌──────────────────────┐
      │ Generate SQL Query   │
      │ (via tool_use)       │
      └────────┬─────────────┘
               ↓
    ┌──────────────────────────┐
    │ Execute Query in MySQL   │
    │ (DatabaseManager)        │
    └────────┬─────────────────┘
             ↓
    ┌──────────────────────────┐
    │ Return Results to LLM    │
    │ (Tool result)            │
    └────────┬─────────────────┘
             ↓
    ┌──────────────────────────┐
    │ LLM Analyzes Results     │
    │ Generates Natural Answer │
    └────────┬─────────────────┘
             ↓
    ┌──────────────────────────┐
    │ Format & Display Result  │
    │ (CLI displays answer)    │
    └──────────────────────────┘
```

### 3.2 Configuration Management Flow

```
Application Start
    ↓
┌─────────────────────────────────┐
│ Check config.json exists?       │
├─ Yes → Load from file           │
└─ No → Load from env variables   │
    ↓
Check API Key Configured?
├─ No → Prompt config_model()
└─ Yes → Continue
    ↓
Check Database Exists?
├─ No → Prompt config_add()
└─ Yes → Set current_database
    ↓
Ready for queries
```

## 4. Multi-Model Support Design

### 4.1 Provider Integration

Each provider is handled through dedicated methods:

| Provider | Integration | Key Feature |
|----------|-------------|------------|
| **Anthropic** | Tool Use + Agent Loop | Reliable SQL generation |
| **Qwen** | Direct prompting | Fast, Chinese-friendly |
| **Zhipu** | Chat completion | Strong reasoning |

### 4.2 Adding New Providers

To add a new provider (e.g., OpenAI):

1. **Update config.py**:
   ```python
   # Add to ModelConfig validation
   if provider == "openai":
       model_name = "gpt-4"
   ```

2. **Update agent.py**:
   ```python
   def _init_client(self):
       if provider == "openai":
           from openai import OpenAI
           self.client = OpenAI(api_key=self.model_config.api_key)
   
   def _call_openai(self, user_query: str) -> str:
       # Implementation
   
   def query(self, user_query):
       elif provider == "openai":
           return self._call_openai(user_query)
   ```

3. **Update CLI config_model()** to show new provider option

## 5. Security Considerations

### 5.1 API Key Management
- Keys stored in `config.json` (not in git)
- Alternatively stored in environment variables
- Never logged or printed in console output

### 5.2 SQL Query Safety
- Executed against configured MySQL database
- Only SELECT operations recommended
- Database user should have minimal permissions
- No query modification or injection protection needed (LLM-generated)

### 5.3 Network Security
- Connections use standard MySQL SSL support
- API calls to LLM providers over HTTPS
- Consider firewall rules for database access

## 6. Error Handling Strategy

### Error Types & Handling

```
┌─────────────────────────────────────┐
│ Potential Errors                    │
├─ Configuration errors              │
│  → Display friendly message + help  │
├─ Database connection errors         │
│  → Suggest checking credentials     │
├─ SQL execution errors               │
│  → Show error to LLM for retry      │
├─ API errors                         │
│  → Retry with backoff               │
└─ LLM processing errors              │
   → Request user to rephrase query   │
```

## 7. Performance Considerations

### 7.1 Optimizations
- Schema cached once per agent session
- Connection pooling (via mysql-connector)
- Efficient result formatting
- Result size limiting (first 10 results to LLM)

### 7.2 Scalability Limits
- Single database connection per query
- No query caching between sessions
- LLM API rate limits apply
- MySQL query timeout inherited from server settings

## 8. Testing Strategy

### Unit Test Areas
1. **Config Module**
   - CRUD operations
   - Config file I/O
   - Validation

2. **Database Module**
   - Connection establishment
   - Query execution
   - Schema retrieval

3. **Agent Module**
   - LLM integration
   - Tool handling
   - Error cases

4. **CLI Module**
   - Command parsing
   - User input validation
   - Output formatting

### Integration Tests
- End-to-end query processing
- Multi-turn conversations
- Database switching
- Config persistence

## 9. Extension Points

### 9.1 Future Enhancements
1. **Database Support**: PostgreSQL, SQLite, SQL Server
2. **Caching**: Schema and result caching
3. **Context**: Multi-turn conversation context
4. **Optimization**: Query explanation and optimization
5. **Analytics**: Usage statistics and query logging
6. **Safety**: Query validation and rollback

### 9.2 Plugin Architecture
Consider implementing provider plugins:
```python
class LLMProvider(ABC):
    @abstractmethod
    def query(self, user_query: str, schema: str) -> str:
        pass

class AnthropicProvider(LLMProvider):
    # Implementation
```

## 10. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Pydantic models** | Type safety and validation |
| **Rich library** | Beautiful, user-friendly CLI |
| **ConfigManager** | Centralized config handling |
| **DatabaseManager** | Abstraction of SQL operations |
| **Multi-model support** | Flexibility and cost optimization |
| **Tool Use pattern** | Reliable LLM output handling |
| **Interactive setup** | Low friction for first-time users |

## 11. Code Metrics

| Component | Lines | Complexity | Purpose |
|-----------|-------|-----------|---------|
| config.py | ~110 | Low | Configuration management |
| database.py | ~75 | Low | DB abstraction |
| agent.py | ~180 | Medium | Core NL2SQL logic |
| cli.py | ~190 | Low-Medium | User interaction |
| main.py | ~85 | Low | Program flow |
| **Total** | **~640** | Low-Medium | Full system |

## 12. Deployment Guide

### Requirements
- Python 3.9+
- MySQL 5.7+ or 8.0+
- Network access to LLM API endpoints
- API keys for chosen provider(s)

### Setup Steps
1. Clone/copy project
2. `pip install -r requirements.txt`
3. `python main.py`
4. Follow interactive configuration

### Docker Support (Future)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 13. Glossary

- **NL2SQL**: Natural Language to SQL conversion
- **Tool Use**: LLM ability to call functions/tools
- **Agent Loop**: Iterative process of LLM generating output, calling tools, and refining
- **Schema**: Database structure (tables and columns)
- **Provider**: LLM service provider (Anthropic, Qwen, Zhipu)
- **Pydantic**: Python library for data validation using type hints
