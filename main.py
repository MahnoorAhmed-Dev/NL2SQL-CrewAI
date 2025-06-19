import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai_tools import NL2SQLTool
from langchain_openai import ChatOpenAI

# Step 1: Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Step 2: Create the NL2SQL tool for SQLite
nl2sql = NL2SQLTool(

    db_type="sqlite",
    db_uri="sqlite:///financial_data.db"
)
 # Use the correct relative path


# Step 3: Define the Agent
agent = Agent(
    role="Financial Analyst",
    goal="Answer financial questions using SQLite data",
    backstory="You are an expert at interpreting income statements and financial data.",
    tools=[nl2sql],
    llm=ChatOpenAI(model="gpt-4", temperature=0)
)

# Step 4: Define a Task
task = Task(
    description="Find the total revenue of all companies in the dataset.",
    expected_output="The total revenue as a number.",
    agent=agent
)

# Step 5: Run the Crew
crew = Crew(
    agents=[agent],
    tasks=[task]
)

result = crew.run()
print("\n✅ Query Result:")
print(result)
