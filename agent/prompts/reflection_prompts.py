"""Reflection Prompt Templates for Self-Correction"""

# Prompt for analyzing errors
REFLECTION_PROMPT = """## 执行失败分析

### 错误信息
{error_message}

### 错误分析
{error_analysis}

### 原始 SQL
```sql
{original_sql}
```

### 数据库 Schema
{schema}

### 历史成功查询
{successful_queries}

## 任务
请分析错误原因，生成修正后的 SQL。

输出格式：
1. **错误原因**: [分析为什么出错]
2. **修正方案**: [如何修正]
3. **修正后的 SQL**:
```sql
[修正后的 SQL 语句]
```
"""

# Prompt for error type classification
ERROR_CLASSIFICATION_PROMPT = """分析以下 SQL 错误，判断错误类型：

错误信息：{error_message}
SQL：{sql}

可能的错误类型：
1. syntax_error - SQL 语法错误
2. unknown_column - 字段不存在
3. unknown_table - 表不存在
4. timeout - 查询超时
5. permission_denied - 权限不足
6. other - 其他错误

请输出错误类型和简要分析。
"""

# Prompt for generating correction
CORRECTION_PROMPT = """基于错误分析，修正以下 SQL：

原始 SQL：
{original_sql}

错误：{error}

修正建议：{suggestion}

可用表结构：
{available_tables}

请输出修正后的 SQL，只输出 SQL 语句，不要其他解释。
"""
