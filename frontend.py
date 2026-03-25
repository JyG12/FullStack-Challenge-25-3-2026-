import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.title("Welcome to my App!")

#upload section
st.header("Upload your file")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    files = {
        "uploaded_file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    response = requests.post(f"{BASE_URL}/upload", files=files)

    if response.status_code == 200:
        st.success("File uploaded successfully!")
        st.json(response.json())
    else:
        st.error(f"Upload failed: {response.text}")

#preview
st.header("Preview your data")

file_name = st.text_input("Enter file name (e.g.Titanic-Dataset.csv)")
n = st.number_input("Number of rows", min_value=1, value=5) #display first 5 first

if st.button("Preview"):
    params = {"file_name": file_name, "n": n}
    res = requests.get(f"{BASE_URL}/preview", params=params)

    if res.status_code == 200:
        data = res.json()["preview"]
        st.dataframe(data)
    else:
        st.error(res.text)

#query
st.header("Ask questions here!")

question = st.text_input("Ask a question about your data")

if st.button("Ask"):
    params = {
        "file_name": file_name,
        "question": question
    }

    res = requests.post(f"{BASE_URL}/query", params=params)

    if res.status_code == 200:
        st.success("Answer:")
        st.write(res.json()["answer"])
    else:
        st.error(res.text)

#history
st.header("Look at your history")

if st.button("Show History"):
    res = requests.get(f"{BASE_URL}/history")

    if res.status_code == 200:
        history = res.json()["history"]
        for item in history:
            st.write(f"Q: {item['question']}")
            st.write(f"A: {item['answer']}")
            st.write("---")
    else:
        st.error("Failed to load history")

# feedback section
st.header("Feedback")

rating = st.slider("Rate the answer (1–5)", 1, 5)
comment = st.text_input("Comments/Feedback?")

if st.button("Submit Feedback"):
    res = requests.post(
        f"{BASE_URL}/feedback",
        params={
            "question": question,
            "rating": rating,
            "comment": comment
        }
    )

    if res.status_code == 200:
        st.success("Feedback submitted!")
    else:
        st.error("Failed to submit feedback")