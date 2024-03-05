import streamlit as st
from streamlit.logger import get_logger
import google.generativeai as genai

api_key = "AIzaSyDE8ZCvuO9WxlC7uHYJ75nEk_1O5bVNT5Y"
genai.configure(api_key=api_key)
genai_model = genai.GenerativeModel("gemini-pro")


LOGGER = get_logger(__name__)

def run():

    st.set_page_config(page_title="AI",page_icon=":star:")

    st.header(body="Powered by **:rainbow[Google Gemini]**",divider="rainbow")

    if "message_history" not in st.session_state:
        st.session_state.message_history = []
    
    for message in st.session_state.message_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    sidebar = st.sidebar
    sidebar.caption("Options")

    colours = ("White","Red","Orange","Green","Grey","Blue","Violet","Rainbow")
    colour_choice = sidebar.selectbox(label="Choose a text colour",help="Changes the colour of the text in chat",options=colours)

    for empty_space in range(3):
        sidebar.write(" ")

    random_prompt = sidebar.button(label="**Generate random prompt**",type="primary")

    prompt_input = st.chat_input("Enter prompt here.")

    if random_prompt:
        prompt_input = (genai_model.generate_content("Generate a random prompt for a chatbot from the user's perspective without surrounding the prompt with quotes.")).text

    if prompt_input:

        text_colour = colour_choice.lower()

        with st.chat_message("user"):
            st.markdown(f":{text_colour}[{prompt_input}]")
            st.session_state.message_history.append({"role":"user","content":f":{text_colour}[{prompt_input}]"})
        
        with st.chat_message("ai"):
    
            try:
                with st.spinner("Generating response..."):
                    prompt_response = (genai_model.generate_content(prompt_input)).text

                st.markdown(prompt_response)
                st.session_state.message_history.append({"role":"ai","content":prompt_response})
            
            except:
                st.warning("Inappropriate Prompt Detected.",icon="⚠️")
                st.session_state.message_history.append({"role":"⚠️","content":"**Blocked Prompt**"})    
         
if __name__ == "__main__":
    run()
