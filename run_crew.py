# run_crew.py

from crewai import Agent, Task, Crew
from text_to_sql_tool import TextToSQLTool
from dotenv import load_dotenv
import os

load_dotenv()

# DB connection string
db_uri = "mssql+pyodbc://@DESKTOP-MMH75SJ\\MSSQLSERVER01/DB1?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

# Create the custom tool
sql_tool = TextToSQLTool(db_uri=db_uri)

# Agent
researcher = Agent(
    name="SQL Analyst",
    role="A data analyst who converts text questions to SQL Server queries",
    goal="Answer business-related queries using SQL",
    backstory="You are part of a BI team responsible for accessing and analyzing financial data.",
    tools=[sql_tool],
    allow_delegation=False
)

def run_query_with_the_crew(user_query:str)->str:
        # Task
    task = Task(
        description=user_query,
        expected_output="Answer to the query",
        agent=researcher
    )

# Crew
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        verbose=False
    )

    return crew.kickoff()
