import streamlit as st
from dotenv import load_dotenv
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import firebase_admin
from firebase_admin import credentials, firestore
import faiss
import base64
import tempfile
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.docstore.document import Document

# Load environment variables from .env file
load_dotenv("C:/Users/The Legendary Fafnir/Desktop/Project 1 Pyth/.env")

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred_path = "C:/Users/The Legendary Fafnir/Desktop/Project 1 Pyth/bachelor-e6968-017ad1ed5611.json"
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {'storageBucket': 'bachelor-e6968.appspot.com'})

db = firestore.client()

def load_vectorstore_from_firestore(doc_name):
    doc_ref = db.collection('embeddings').document(doc_name)
    doc = doc_ref.get()
    if doc.exists:
        index_str = doc.to_dict()['index']
        texts = doc.to_dict()['texts']
        index_bytes = index_str.encode('latin1')
        
        # Save the index bytes to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, "wb") as f:
            f.write(index_bytes)
        temp_file.close()
        
        # Deserialize FAISS index from the file
        index = faiss.read_index(temp_file.name)
        
        embeddings = OpenAIEmbeddings()
        # Initialize the docstore with the texts
        documents = [Document(page_content=text) for text in texts]
        docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(documents)})
        index_to_docstore_id = {i: str(i) for i in range(len(documents))}
        
        vectorstore = FAISS(embeddings, index, docstore, index_to_docstore_id)
        return vectorstore
    else:
        st.error("No embeddings found in Firestore.")
        return None

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(f"**User**: {message.content}")
        else:
            st.write(f"**Bot**: {message.content}")

    # Save the question and answer to Firestore under the user's account
    user = st.session_state.get("username", "default_user")
    db.collection('questions_answers').add({
        'user': user,
        'question': user_question,
        'answer': response['chat_history'][-1].content
    })

def app():
    load_dotenv()

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with Teacher PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    if st.session_state.conversation is None:
        with st.spinner("Loading embeddings from Firebase"):
            vectorstore = load_vectorstore_from_firestore("teacher_pdfs")
            if vectorstore:
                st.session_state.conversation = get_conversation_chain(vectorstore)
                st.success("Embeddings loaded and processed successfully!")

if __name__ == '__main__':
    app()
