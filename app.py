import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.exceptions import (CredentialsError,ForgotError,LoginError,RegisterError,ResetError,UpdateError) 
from streamlit_extras.switch_page_button import switch_page
import pickle

#  https://docs.kanaries.net/topics/Streamlit/streamlit-authentication
# Loading config file


if 'auth' not in st.session_state:
    st.session_state['auth'] = ''
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = ''

st.session_state["authentication_status"] = None
st.session_state['logged_in'] = False

filehandler = open(b"login_state.pkl","wb")
pickle.dump(st.session_state['logged_in'],filehandler)

with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)
st.session_state['auth'] = authenticator
# Creating a login widget
try:
    a = authenticator.login()
    print(a)
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.session_state["logged_in"] = True
    filehandler = open(b"login_state.pkl","wb")
    pickle.dump(st.session_state['logged_in'],filehandler)
    switch_page("page_0")
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

st.subheader("CONFIDENTIALITY NOTICE:  This Dashboard, its analysis and any accompanying data / documents contain information belonging to the San Bernardino Public Defender's Office which may be confidential and legally bounded by The work product doctrine. This information is only for the use of the individual or entity to which it was intended.")



