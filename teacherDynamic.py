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
import tempfile
import openai
import json
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.docstore.document import Document
from openai import OpenAI

# Load environment variables from .env file
load_dotenv("C:/Users/The Legendary Fafnir/Desktop/Project 1 Pyth/.env")

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred_path = "C:/Users/The Legendary Fafnir/Desktop/Project 1 Pyth/bachelor-e6968-017ad1ed5611.json"
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {'storageBucket': 'bachelor-e6968.appspot.com'})

db = firestore.client()

# Function to load vectorstore from Firestore
def load_vectorstore_from_firestore(doc_name):
    doc_ref = db.collection('embeddings').document(doc_name)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        index_str = data['index']
        texts = data['texts']
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

# Function to get a conversational chain
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

# Function to generate dynamic answer
def generate_dynamic_answer(question):
    response = st.session_state.conversation({'question': question})
    return response['chat_history'][-1].content

# Function to generate image based on text
def generate_image_from_text(prompt):
    client = openai.OpenAI()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

# Function to display titles, dynamic answers, and generated images
def display_titles_and_dynamic_answers(data):
    for item in data:
        title = item['Title']
        question = item['question']
        st.markdown(f"## {title}")
        if 'conversation' in st.session_state:
            answer = generate_dynamic_answer(question)
            st.markdown(answer)
            image_url = generate_image_from_text(answer)
            st.image(image_url)
        else:
            st.warning("Conversation chain not initialized.")
        st.markdown("***")

def load_questions_titles(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def app():
    openai.api_key = os.getenv("OPENAI_API_KEY")

    st.title("Dynamic Lecture Questions")

    pdf_option = st.selectbox("Select a PDF", ["dbs-1-1.pdf", "dbs-2.pdf"])

    if pdf_option == "dbs-1-1.pdf":
        data = load_questions_titles("dbs-1-1.json")
    elif pdf_option == "dbs-2.pdf":
        data = load_questions_titles("dbs-2.json")

    if data:
        vectorstore = load_vectorstore_from_firestore("teacher_pdfs")
        if vectorstore:
            st.session_state.conversation = get_conversation_chain(vectorstore)
            display_titles_and_dynamic_answers(data)
        else:
            st.error("Failed to load vectorstore.")

if __name__ == "__main__":
    app()
