from snowflake.snowpark import Session
import snowflake.snowpark as snowpark
import streamlit as st
connection_parameters = {
   "account": "qpgirsc-cr13281",
    "user": "FLIGHT505",
    "password": "joXfyt-zojwom-behsi2",
    "role": "ACCOUNTADMIN",  # optional
   "warehouse": "COMPUTE_WH",  # optional
   "database": "STREAMLIT",  # optional
   "schema": "MEMBER_APPLICATION",  # optional
  }  