import sqlite3
from dotenv import load_dotenv
import os
from crewai import Agent
from crewai import Task
from crewai import Crew
from langchain_openai import ChatOpenAI
from crewai_tools import FileWriterTool
import pandas as pd

from crewai_tools import NL2SQLTool




# Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


# csv and sqllite integration
csv_file = "Annual_P_L_1_final.csv"
db_file = "financial_data.db"
table_name = "companies"

# Connect to database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Check if table already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
table_exists = cursor.fetchone()

if not table_exists:
    print("[🟢] Table not found. Loading CSV into database...")
    df = pd.read_csv(csv_file)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print("[✅] Table created and data loaded.")
else:
    print("[⚠️] Table already exists. Skipping CSV import.")

conn.commit()
conn.close()


# NL2SQL setup
nl2sql=NL2SQLTool(db_url="sqlite:///financial_data.db")


# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Defining Agents
researcher=Agent(
  role='Senior Research Analyst',
  goal='Uncover cutting edge developments in AI and machine learning',
  backstory="""You are an AI expert with a deep understanding if the latest advancements in AI and machine learning.
  You excel at researching complex topics and synthesizing information into clear concise reports.""",
  verbose=True,
  allow_delegation=False,
  llm=llm
)

writer=Agent(
  role='Tech Writer',
  goal='Crafting compelling articles based on research findings',
  backstory="""You are a complex writer with a knack for explaining complex topics in an engaging and excessible way.
  You can turn research into high quality articles.""",
  verbose=True,
  allow_delegation=False,
  llm=llm
  

)

# Assigning Tasks

research_task=Task(
  description="""Conduct in-depth research on the latest development in generative AI.
  Focus on new technologies, archaetectures and applications.""",
  expected_output="A detailed report summarizing the current state of generative AI, including key technologies, use cases, and trends.",

  agent=researcher

)

writing_task=Task(
  description="""Based on the research write a compelling article about the latest advancements in generative AI.
  Include key takeaways and potential future directions.""",
  expected_output="A well-structured article that explains recent developments in generative AI in a clear and engaging way.",

  agent=writer,
  depends_on=[research_task]

)

# Creating the Crew
crew=Crew(
  agents=[researcher,writer],
  tasks=[research_task,writing_task],
  verbose=False

)

results = crew.kickoff()
result_text = str(results)

# Initialize FileWriterTool
file_writer_tool = FileWriterTool()

# Correct call using run() with keyword arguments
file_write_result = file_writer_tool.run(
    filename='crew_output.txt',
    content=result_text,
    directory='.',
    overwrite=True     
)

print(file_write_result)