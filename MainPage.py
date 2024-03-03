import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def run():

    st.set_page_config(page_title="AI",page_icon=":star:")

    st.header(body="Powered by **:rainbow[Google Gemini]**",divider="rainbow")

    colours = ("white","red","orange","green","grey","rainbow")
    colour_choice = st.sidebar.selectbox(label="Choose a text colour",help="Changes the colour of the text in chat",options=colours)

    prompt_input = st.chat_input("Enter prompt here.")

    if prompt_input:
         with st.chat_message("user"):
            st.markdown(f":{colour_choice}[{prompt_input}]")
         
if __name__ == "__main__":
    run()
