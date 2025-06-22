from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Any
from sqlalchemy import create_engine, text
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class TextToSQLInput(BaseModel):
    query: str = Field(description="User's natural language query.")


class TextToSQLTool(BaseTool):
    name: str = "TextToSQLTool"
    description: str = "Takes natural language input and returns SQL results."
    args_schema: Type[BaseModel] = TextToSQLInput

    db_uri: str

    def _run(self, query: str) -> str:
        engine = create_engine(self.db_uri)
        try:
            schema = self.get_schema(engine)
            prompt = self.build_prompt(query, schema)
            sql = self.call_llm(prompt)
            print(f"🔎 Generated SQL:\n{sql}")
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                if result.returns_rows:
                    rows = result.fetchall()
                    cols = result.keys()

                    if not rows:
                        return "No results found."

                    # Calculate max width for each column
                    col_widths = [len(col) for col in cols]
                    for row in rows:
                        for i, item in enumerate(row):
                            col_widths[i] = max(col_widths[i], len(str(item)))

                    # Build header
                    header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(cols))
                    divider = "-+-".join("-" * col_widths[i] for i in range(len(cols)))

                    # Build rows
                    data_rows = [
                        " | ".join(str(item).ljust(col_widths[i]) for i, item in enumerate(row))
                        for row in rows
                    ]

                    output = f"{header}\n{divider}\n" + "\n".join(data_rows)
                    return output.strip()
                return "✅ SQL executed successfully."
        except Exception as e:
            return f"❌ Failed: {e}"

    def get_schema(self, engine):
        with engine.connect() as conn:
            tables = conn.execute(text(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
            )).fetchall()
            schema = {}
            for (table,) in tables:
                cols = conn.execute(text(
                    f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'"
                )).fetchall()
                schema[table] = [f"{c} ({t})" for c, t in cols]
            return schema

    def build_prompt(self, query, schema):
        schema_str = "\n".join(f"{t}: {', '.join(c)}" for t, c in schema.items())
        return f"""You are a SQL assistant. Given the schema and question, write a valid SQL Server query.

Schema:
{schema_str}

Question:
{query}

SQL:
"""

    def call_llm(self, prompt: str):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
