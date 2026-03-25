# FullStack-Challenge-25-3-2026-
Developing an AI powered app to upload files, display top N rows, and keep a history of prompts

Features:
1. File upload
- uploads csv/excel files
- files are processed and stored in-memory using FastAPI

2. Data preview
- view top N rows of uploaded datasets
- user-defined parameter

3. Ask questions
- users can ask questions about the data
  
4. Prompt history
- stores users' queries and responses

5. Feedback system
- users can rate responses from 1-5
- optional comments/feedback


Backend - FastAPI, Pandas, Python
Frontend - Streamlit, RestAPIs via HTTP requests


Requirements:
pip install fastapi uvicorn pandas streamlit python-multipart requests



