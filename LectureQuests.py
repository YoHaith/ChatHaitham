import streamlit as st
import json
import os

def load_questions_answers(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def display_titles_and_answers(data):
    for item in data:
        title = item['Title']
        answer = item['answer']
        st.markdown(f"## {title}")
        st.markdown(answer)
        st.markdown("***")

def app():
    st.title("Lecture Answers")

    # Dropdown to select the PDF
    pdf_option = st.selectbox("Select a PDF", ["dbs-1-1.pdf", "dbs-2.pdf"])

    if pdf_option == "dbs-1-1.pdf":
        data = load_questions_answers("dbs-1-1.json")
    elif pdf_option == "dbs-2.pdf":
        data = load_questions_answers("dbs-2.json")

    if data:
        display_titles_and_answers(data)
        
        # Show images if dbs-1-1.pdf is selected
        if pdf_option == "dbs-1-1.pdf":
            image_paths = [
                "C:/Users/The Legendary Fafnir/Desktop/Project 1 Pyth/dbs1 a.jpeg",
                "C:/Users/The Legendary Fafnir/Desktop/Project 1 Pyth/dbs1 b.jpeg"
            ]
            for image_path in image_paths:
                if os.path.exists(image_path):
                    st.image(image_path)
                else:
                    st.warning(f"Image not found: {image_path}")

if __name__ == "__main__":
    app()
