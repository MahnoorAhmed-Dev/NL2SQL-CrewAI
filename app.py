import streamlit as st
from run_crew import run_query_with_the_crew

st.set_page_config(page_title="NLP to SQL", layout="centered")

st.title("Natural Language to SQL Analyst")
st.subheader("Query Your SQL Table")

user_input=st.text_area("Enter Your Question",  placeholder="List all the industries?", height=100)

if st.button("Run Query"):
  if user_input.strip()=="":
    st.warning("Warning: Please enter a query")

  else:
    with st.spinner("Querying your DB"):
         result= run_query_with_the_crew(user_input)
         st.success("Query Executed")
         st.code(result, language="text")

