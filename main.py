import streamlit as st
from streamlit_option_menu import option_menu
import account, TeacherPdfs, yourHistory, NewPdfs, allHistory, LectureQuests, teacherDynamic

st.set_page_config(
    page_title="Ask any question",
)

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title='Ask any question',
                options=['Account', 'Lecture Questions', 'Teacher Dynamic', 'Chat with Lectures', 'Chat with New PDFs', 'Your History', 'All the History'],
                icons=['person-circle', 'question-circle', 'file-earmark-fill', 'chat-fill', 'chat-text-fill'],
                menu_icon='chat-text-fill',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        if app == "Account":
            account.app()
        elif app == "Lecture Questions":
            LectureQuests.app()
        elif app == "Teacher Dynamic":
            teacherDynamic.app()
        elif app == "Chat with Teacher PDFs":
            TeacherPdfs.app()
        elif app == 'Chat with New PDFs':
            NewPdfs.app()
        elif app == 'Your History':
            yourHistory.app()
        elif app == 'All the History':
            allHistory.app()

if __name__ == "__main__":
    app = MultiApp()
    app.run()
