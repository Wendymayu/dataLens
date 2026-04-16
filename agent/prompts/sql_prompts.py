"""SQL-related prompt templates"""

# Prompt for generating SQL from natural language
SQL_GENERATION_PROMPT = """Database Schema:
{schema}

User Query: {user_query}

Generate a SQL query to answer the user's question. Follow these rules:
1. Only use SELECT, SHOW, DESCRIBE, or EXPLAIN statements
2. Use appropriate table aliases
3. Apply correct WHERE conditions based on the user's intent
4. Limit results if the query might return many rows"""

# Prompt for interpreting SQL results
SQL_RESULT_INTERPRET_PROMPT = """SQL执行成功，返回 {result_count} 条记录，结果如下（最多显示10条）：
{results}

请用自然语言总结这些结果。注意：
1. 在回复中不要重复显示SQL代码块
2. 直接回答用户的问题
3. 如果有数据，给出具体的数字和洞察"""