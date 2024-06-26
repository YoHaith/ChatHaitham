import streamlit as st
from firebase_admin import firestore

def app():
    db = firestore.client()

    try:
        username = st.session_state['username']
        st.title('History of Questions and Answers for: ' + username)

        # Retrieve the user's questions and answers from Firestore
        docs = db.collection('questions_answers').where('user', '==', username).stream()
        history = [(doc.to_dict()['question'], doc.to_dict()['answer']) for doc in docs]

        if history:
            for question, answer in history:
                st.write(f"**Question**: {question}")
                st.write(f"**Answer**: {answer}")
                st.write("---")
        else:
            st.write("No history found.")
            
    except KeyError:
        st.write("Please log in first.")

if __name__ == "__main__":
    app()
