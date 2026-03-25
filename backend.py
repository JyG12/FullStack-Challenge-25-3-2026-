from fastapi import FastAPI, UploadFile, HTTPException
import pandas as pd
import numpy as np
import io

app = FastAPI()

allowed_format = [
    "text/csv",
    "application/vnd.ms-excel",  # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # .xlsx
]

file_store = {}

#1. Upload file and store in memory
@app.post('/upload')
async def upload_file(uploaded_file: UploadFile):
    if uploaded_file.content_type not in allowed_format:
        raise HTTPException(status_code=400, detail="Only CSV/.xls/.xlsx format allowed!")

    try:
        data = await uploaded_file.read()

        if uploaded_file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(data))

        elif uploaded_file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(data))

        else:
            raise HTTPException(status_code=400, detail="Unsupported file extension.")

        file_store[uploaded_file.filename] = df
        
        return {
            "file_name": uploaded_file.filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "preview": df.head(10).replace({np.nan: None}).to_dict(orient="records")
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

#2. Display top N rows
@app.get('/preview')
def preview(file_name: str, sheet_name: str = None, n: int = 5):
    if file_name not in file_store:
        raise HTTPException(status_code=404, detail="File not found!")
    
    data = file_store[file_name] #retrieve what was uploaded earlier
    
    if isinstance(data, pd.DataFrame): #if data is a df, its CSV
        df = data

    else: #excel
        if sheet_name not in data:
            raise HTTPException(status_code=400, detail="Invalid sheet name")
        df = data[sheet_name]

    #clean the data
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.astype(object)  
    df = df.where(pd.notnull(df), None)

    return {
        "file": file_name,
        "sheet": sheet_name,
        "rows_requested": n,
        "preview": df.head(n).to_dict(orient="records")
    }
    
    
#3. query
from openai import OpenAI
import os
from datetime import datetime
api_key="#type here"

client = OpenAI(api_key=api_key)


#post a query
@app.post('/query')
def query(file_name: str, sheet_name: str = None, question: str = ""):

    if file_name not in file_store:
        raise HTTPException(status_code=404, detail="File not found")

    df = file_store[file_name]


    try:
        # limit
        df_sample = df.head(20).to_string()

        prompt = f"""
You are a data analyst.

Here is a dataset (first 20 rows):
{df_sample}

User question:
{question}

Only use the data provided to you.
If you are unsure, return "insufficient data"
Be concise and accurate! Answer the question clearly. If any calculation is needed, explain your steps clearly
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        result = response.output_text

        # save history
        queryhistory.append({
            "file": file_name,
            "question": question,
            "answer": result,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "question": question,
            "answer": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
queryhistory = []


@app.get('/history')
def gethistory():
    return {"history":queryhistory}

#feedback
from typing import List
feedback: List[dict] = []

@app.post('/feedback')
def sumit_feedback(question:str, rating:int, comment:str):
    feedback_entry = {
        "question":question,
        "rating": rating,
        "comment": comment
    }

    feedback.append(feedback_entry)
    
    return {
        "message":"Thank you for your feedback, we have received it!",
        "no_of_feedbacks": len(feedback)
    }
    
@app.get('/feedback')
def get_feedback():
    return {"feedback":feedback}