import streamlit as st
from streamlit.logger import get_logger
import google.generativeai as genai
from pypdf import PdfReader

api_key = "AIzaSyDE8ZCvuO9WxlC7uHYJ75nEk_1O5bVNT5Y"
genai.configure(api_key=api_key)
genai_model = genai.GenerativeModel("gemini-pro")


LOGGER = get_logger(__name__)

def prompt(prompt_input,colour="white"):

    with st.chat_message("user"):
        st.markdown(f":{colour}[{prompt_input}]")
        st.session_state.message_history.append({"role":"user","content":f":{colour}[{prompt_input}]"})

    return prompt_input

def generate_response(prompt_input,role="ai",subtracted_index=1):

    history = ""

    for message in range(len(st.session_state.message_history)-subtracted_index):
        first_bracket = st.session_state.message_history[message]["content"].find("[")
        content = (st.session_state.message_history[message]["content"])[first_bracket+1:-1]
        history += content + "\n"

    
    with st.chat_message(role):
    
        try:
            with st.spinner("Generating response..."):
                prompt_response = (genai_model.generate_content(history+prompt_input)).text

                st.markdown(prompt_response)
                st.session_state.message_history.append({"role":role,"content":prompt_response})
                return prompt_response
        except:
            st.warning("Inappropriate Prompt Detected.",icon="⚠️")
            st.session_state.message_history.append({"role":"⚠️","content":"**Blocked Prompt**"})

    

def clear_state():
    st.session_state.message_history.clear()
    st.rerun()

def run():

    st.set_page_config(page_title="Gemini",page_icon=":star:")

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

    sidebar.divider()

    random_prompt = sidebar.button(label=":green[**Generate random prompt**]",type="secondary")
    bot_to_bot = sidebar.button(label=":green[**Bot-To-Bot Convo**]")

    if bot_to_bot:

        st.session_state.message_history.clear()
        
        second = "greet an ai bot"
        
        while True:
         
            first = generate_response(second,role="🔴",subtracted_index=0)
                
            second = generate_response(first,role="🔵",subtracted_index=0)

          

    sidebar.divider()

    pdf_file = sidebar.file_uploader(label="Upload a PDF file",type="pdf")
    get_info = sidebar.button("**Get Info**",type="secondary")

    if pdf_file:
        pdf_file_reader  = PdfReader(pdf_file)

        if get_info:
            all_data = ""

            
            for page in range(pdf_file_reader._get_num_pages()):
                current_page = pdf_file_reader.pages[page]
                all_data += current_page.extract_text()
        
            
            st.info(f"PDF File: {pdf_file.name}",icon="ℹ️")
            st.session_state.message_history.append({"role":"ℹ️","content":f"**PDF File: {pdf_file.name}**"})
            
            generate_response(f"Give some detailed information about the text below.\n\n{all_data}")
        
    
    sidebar.divider()

    delete_message_history = sidebar.button(label="**Delete Message History**",type="primary")

    if delete_message_history:
        
        clear_state()
        

    prompt_input = st.chat_input("Enter prompt here.")


    if random_prompt:
        with st.spinner("Generating random prompt..."):
            prompt_input = (genai_model.generate_content("Generate a random prompt for a chatbot from the user's perspective without surrounding the prompt with quotes.")).text

    if prompt_input:

        text_colour = colour_choice.lower()

        prompt(prompt_input,text_colour)
        
        generate_response(prompt_input)
               
            
         
if __name__ == "__main__":
    run()
