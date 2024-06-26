import streamlit as st
import firebase_admin
from firebase_admin import credentials
import pyrebase

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyAjwydXqlL4uaz33l4PUlhxpcPX9pSR_cs",
    "authDomain": "bachelor-e6968.firebaseapp.com",
    "databaseURL": "https://bachelor-e6968.firebaseio.com",
    "projectId": "bachelor-e6968",
    "storageBucket": "bachelor-e6968.appspot.com",
    "messagingSenderId": "485151394643",
   # "appId": "your_app_id",
   # "measurementId": "your_measurement_id"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

cred = credentials.Certificate('bachelor-e6968-017ad1ed5611.json')
# firebase_admin.initialize_app(cred)

def app():
    st.title('Welcome to :violet[the Kingdom] :sunglasses:')

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    def login(email, password):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.write('Login Successful')

            user_info = auth.get_account_info(user['idToken'])
            st.session_state.username = user_info['users'][0]['localId']
            st.session_state.useremail = user_info['users'][0]['email']

            st.session_state.signout = True
            st.session_state.signedout = True

        except:
            st.warning('Login Failed')

    def logout():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ''
        st.session_state.useremail = ''

    if 'signedout' not in st.session_state:
        st.session_state.signedout = False
    if 'signout' not in st.session_state:
        st.session_state.signout = False

    if not st.session_state['signedout']:
        choice = st.selectbox('Login/signup', ['Login', 'Sign Up'])

        if choice == 'Login':
            email = st.text_input('Email address')
            password = st.text_input('Password', type='password')

            st.button('Login', on_click=lambda: login(email, password))

        else:
            email = st.text_input('Email address')
            password = st.text_input('Password', type='password')
            username = st.text_input('Enter your unique username')

            if st.button('Create my account'):
                try:
                    user = auth.create_user_with_email_and_password(email, password)
                    auth.update_profile(user['idToken'], display_name=username)
                    st.success('Account created successfully')
                    st.markdown('Please login using your email and password')
                    st.balloons()
                except:
                    st.error('Account creation failed')

    if st.session_state.signout:
        st.text('Name: ' + st.session_state.username)
        st.text('Email id: ' + st.session_state.useremail)
        st.button('Sign out', on_click=logout)
