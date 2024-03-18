import streamlit as st
from streamlit.logger import get_logger
import google.generativeai as genai
from pypdf import PdfReader
import PIL.Image


api_key = "AIzaSyDE8ZCvuO9WxlC7uHYJ75nEk_1O5bVNT5Y"
genai.configure(api_key=api_key)

genai_text_model = genai.GenerativeModel("gemini-pro")
genai_vision_model = genai.GenerativeModel("gemini-pro-vision")

LOGGER = get_logger(__name__)

def prompt(prompt_input,colour="white"):

    with st.chat_message("user"):
        st.markdown(f":{colour}[{prompt_input}]")
        st.session_state.message_history.append({"role":"user","content":f":{colour}[{prompt_input}]","isBlocked":False})


def generate_response(prompt_input):

    context_history = ""

    for message in range(len(st.session_state.message_history)-1):

        if st.session_state.message_history[message]["isBlocked"] == True:
            continue

        first_bracket = st.session_state.message_history[message]["content"].find("[")
        content = (st.session_state.message_history[message]["content"])[first_bracket+1:-1]

        context_history += content + "\n"

    
    with st.chat_message("ai"):
    
        try:
            with st.spinner("Generating response..."):
                prompt_response = (genai_text_model.generate_content(context_history+prompt_input)).text

                st.markdown(prompt_response)
                st.session_state.message_history.append({"role":"ai","content":prompt_response,"isBlocked":False})
                
        except:
            st.warning("Inappropriate Prompt Detected.",icon="⚠️")
            st.session_state.message_history.append({"role":"ai","content":"blocked","isBlocked":True})
            st.session_state.message_history[-2]["isBlocked"] = True
    

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

            if message["content"] == "image":
                st.image(message["file"])

            elif message["content"] == "blocked":
                st.warning("Inappropriate Prompt Detected.",icon="⚠️")

            else:
                st.markdown(message["content"])

    sidebar = st.sidebar
    sidebar.caption("Options")

    colours = ("White","Red","Orange","Green","Grey","Blue","Violet","Rainbow")
    colour_choice = sidebar.selectbox(label="Choose a text colour",help="Changes the colour of the text in chat",options=colours)
    
    sidebar.divider()

    pdf_file = sidebar.file_uploader(label="Upload a PDF file",type="pdf",help="Upload a PDF file for Gemini to analyse")
    get_pdf_info = sidebar.button("**Get PDF Info**",type="secondary")
    img_file = sidebar.file_uploader(label="Upload an image file",type=["png","jpg","jpeg"],help="Upload an IMG file for Gemini to analyse")
    get_img_info = sidebar.button("**Get IMG Info**",type="secondary")

    if pdf_file and get_pdf_info:

        pdf_file_reader  = PdfReader(pdf_file)
        all_data = ""
            
        for page in range(pdf_file_reader._get_num_pages()):
            current_page = pdf_file_reader.pages[page]
            all_data += current_page.extract_text()
        
            
        st.info(f"PDF File: {pdf_file.name}",icon="ℹ️")
        st.session_state.message_history.append({"role":"ℹ️","content":f"**PDF File: {pdf_file.name}**","isBlocked":False})
            
        generate_response(f"Give some detailed information about the text below.\n\n{all_data}")
        
    
    if img_file and get_img_info:

        st.info(f"IMG File: {img_file.name}", icon="ℹ️")
        st.session_state.message_history.append({"role":"ℹ️","content":f"**IMG File: {img_file.name}**","isBlocked":False})

        usabled_img_file = PIL.Image.open(img_file)

        with st.chat_message("user"):
            st.image(image=img_file)

        img_info = (genai_vision_model.generate_content(usabled_img_file)).text

        st.session_state.message_history.append({"role":"user","content":"image","isBlocked":False,"file":img_file})
        st.session_state.message_history.append({"role":"ai","content":img_info,"isBlocked":False})
        
        with st.chat_message("ai"):
            with st.spinner("Generating response..."):
                st.markdown(img_info)

    sidebar.divider()

    random_prompt = sidebar.button(label=":blue[**Generate random prompt**]",type="secondary")
    delete_message_history = sidebar.button(label="**Delete Message History**",type="primary")

    if delete_message_history:
        
        clear_state()
  
    
    prompt_input = st.chat_input("Enter prompt here.")
    

    if random_prompt:
        with st.spinner("Generating random prompt..."):
            prompt_input = (genai_text_model.generate_content("Generate a random prompt for a chatbot from the user's perspective without surrounding the prompt with quotes.")).text

    if prompt_input:

        text_colour = colour_choice.lower()

        prompt(prompt_input,text_colour)
        
        generate_response(prompt_input)
               
            
         
if __name__ == "__main__":
    run()
