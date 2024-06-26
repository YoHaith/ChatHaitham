import streamlit as st
from firebase_admin import firestore

def app():
    db = firestore.client()

    st.title("All the History")

    # Retrieve all users' questions and answers from Firestore
    docs = db.collection('questions_answers').stream()
    history = [(doc.to_dict()['user'], doc.to_dict()['question'], doc.to_dict()['answer']) for doc in docs]

    if history:
        for user, question, answer in history:
            st.write(f"**User**: {user}")
            st.write(f"**Question**: {question}")
            st.write(f"**Answer**: {answer}")
            st.write("---")
    else:
        st.write("No history found.")

if __name__ == "__main__":
    app()
