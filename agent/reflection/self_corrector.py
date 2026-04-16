"""Self Corrector - Automatic SQL correction based on error analysis"""

import re
import json
from typing import Dict, Any, Optional, List

from agent.reflection.error_analyzer import ErrorAnalyzer


class SelfCorrector:
    """
    Automatically correct SQL based on error analysis
    """

    def __init__(self, model_config: Any, provider: str = "openai-compatible"):
        """
        Initialize corrector

        Args:
            model_config: Model configuration
            provider: LLM provider type
        """
        self.model_config = model_config
        self.provider = provider.lower()
        self.error_analyzer = ErrorAnalyzer()
        self._init_client()

    def _init_client(self):
        """Initialize LLM client"""
        if self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.model_config.api_key)
        elif self.provider in ("openai-compatible", "qwen", "zhipu"):
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.model_config.api_key,
                base_url=getattr(self.model_config, 'base_url', None)
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def correct_sql(
        self,
        sql: str,
        error: str,
        schema: str,
        max_attempts: int = 2
    ) -> Optional[str]:
        """
        Attempt to correct SQL based on error

        Args:
            sql: Original SQL that caused error
            error: Error message from execution
            schema: Database schema for reference
            max_attempts: Maximum correction attempts

        Returns:
            Corrected SQL or None if cannot correct
        """
        # Analyze error first
        analysis = self.error_analyzer.analyze(error)

        # Only attempt correction for retriable errors
        if not self.error_analyzer.is_retriable(analysis["error_type"]):
            return None

        # Try quick fixes first
        quick_fix = self._try_quick_fix(sql, analysis)
        if quick_fix and quick_fix != sql:
            return quick_fix

        # Use LLM for more complex corrections
        corrected = await self._llm_correct(sql, analysis, schema)

        return corrected

    def _try_quick_fix(self, sql: str, analysis: Dict[str, Any]) -> Optional[str]:
        """
        Try quick fixes for common errors

        Args:
            sql: Original SQL
            analysis: Error analysis result

        Returns:
            Quick fixed SQL or None
        """
        error_type = analysis["error_type"]
        matched_text = analysis.get("matched_text", "")

        if error_type == "unknown_column":
            # Try to fix common column name mistakes
            return self._fix_unknown_column(sql, matched_text)

        elif error_type == "syntax_error":
            # Try to fix common syntax mistakes
            return self._fix_syntax_error(sql)

        return None

    def _fix_unknown_column(self, sql: str, unknown_col: str) -> Optional[str]:
        """Attempt to fix unknown column error"""
        # Common column name variations
        variations = {
            "id": ["ID", "Id", "user_id", "id"],
            "name": ["Name", "NAME", "username", "user_name"],
            "email": ["Email", "EMAIL", "email_address"],
            "time": ["Time", "TIME", "created_at", "create_time", "timestamp"],
        }

        unknown_lower = unknown_col.lower()
        for standard, variants in variations.items():
            if unknown_lower in [v.lower() for v in variants]:
                # Try replacing with standard form
                pattern = re.compile(re.escape(unknown_col), re.IGNORECASE)
                return pattern.sub(standard, sql)

        return None

    def _fix_syntax_error(self, sql: str) -> Optional[str]:
        """Attempt to fix common syntax errors"""
        corrected = sql

        # Fix missing space after comma
        corrected = re.sub(r',(\w)', r', \1', corrected)

        # Fix double spaces
        corrected = re.sub(r'\s+', ' ', corrected)

        # Fix missing space before WHERE
        corrected = re.sub(r'(\w)WHERE', r'\1 WHERE', corrected, flags=re.IGNORECASE)

        # Fix trailing semicolon issues (add or remove)
        corrected = corrected.strip().rstrip(';')

        if corrected != sql:
            return corrected
        return None

    async def _llm_correct(
        self,
        sql: str,
        analysis: Dict[str, Any],
        schema: str
    ) -> Optional[str]:
        """
        Use LLM to correct SQL

        Args:
            sql: Original SQL
            analysis: Error analysis
            schema: Database schema

        Returns:
            Corrected SQL or None
        """
        correction_prompt = f"""分析并修正以下 SQL 错误：

原始 SQL：
```sql
{sql}
```

错误信息：{analysis['raw_error']}
错误类型：{analysis['error_type']}
建议：{analysis['suggestion']}

数据库结构：
{schema[:1000]}

请输出修正后的 SQL，只输出 SQL 语句，不要其他解释。
只使用 SELECT/SHOW/DESCRIBE/EXPLAIN 语句。
"""

        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_config.model_name,
                    max_tokens=500,
                    messages=[{"role": "user", "content": correction_prompt}]
                )
                result = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model_config.model_name,
                    messages=[{"role": "user", "content": correction_prompt}],
                    temperature=0.3,
                    max_tokens=500
                )
                result = response.choices[0].message.content

            # Extract SQL from response
            corrected = self._extract_sql(result)
            return corrected if corrected and corrected != sql else None

        except Exception as e:
            # If LLM correction fails, return None
            return None

    def _extract_sql(self, text: str) -> Optional[str]:
        """Extract SQL from text response"""
        # Try code block first
        code_block = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
        if code_block:
            return code_block.group(1).strip()

        # Try generic code block
        code_block = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if code_block:
            sql = code_block.group(1).strip()
            if sql.upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                return sql

        # Try direct extraction
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                return line.rstrip(';')

        return None
