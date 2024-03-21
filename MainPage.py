# Import the needed libraries
import streamlit as st, PIL.Image, time, os
from streamlit.logger import get_logger
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Access the API KEY from the environment variable and configure it to access Gemini
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

# Access a gemini model for text and for vision
genai_text_model = genai.GenerativeModel("gemini-pro")
genai_vision_model = genai.GenerativeModel("gemini-pro-vision")

LOGGER = get_logger(__name__)

# Function to display user's prompt with the colour and to store the prompt in the message history
def prompt(prompt_input,colour="white"):
    # Use a "user" icon to display the user prompt
    with st.chat_message("user"):
        # Display the prompt alongside it's colour
        st.markdown(f":{colour}[{prompt_input}]")
        # Append the prompt with the user as the role and allow it to be accessed in the context history 
        st.session_state.message_history.append({"role":"user","content":f":{colour}[{prompt_input}]","isBlocked":False})

# Function to generate a response based on a prompt
def generate_response(prompt_input,role="ai"):
    # Store the context history based on the message history
    context_history = ""
    # Loop through the message history
    for message in range(len(st.session_state.message_history)-1):
        # If a message is blocked, skip it
        if st.session_state.message_history[message]["isBlocked"] == True:
            continue
        # If a message's content contains colours, remove the colour from the content
        first_bracket = st.session_state.message_history[message]["content"].find("[")
        content = (st.session_state.message_history[message]["content"])[first_bracket+1:-1]
        # Add the content to the context history
        context_history += content + "\n\n"
    
    # Use an "AI" icon to display the generated resposne
    with st.chat_message(role):
        # Handle any exceptions related to disallowed prompt
        try:
            # While the text is being generated, use a spinner status
            with st.spinner("Generating response..."):
                # Store the generated response in a variable
                prompt_response = (genai_text_model.generate_content(context_history+prompt_input)).text
                # Display the generated response and store it in the message history
                st.markdown(prompt_response)
                st.session_state.message_history.append({"role":role,"content":prompt_response,"isBlocked":False})
                return prompt_response
        # Catch any exceptions    
        except:
            # Throw a warning to the user
            st.warning("Inappropriate Prompt Detected.",icon="⚠️")
            # Store the warning to the message history and block the prompt & the response from being considered in the context history
            st.session_state.message_history.append({"role":role,"content":"blocked","isBlocked":True})
            st.session_state.message_history[-2]["isBlocked"] = True
    

         
# Function to clear the message history and clear the screen
def clear_state():
    st.session_state.message_history.clear()
    st.rerun()

# Main function that will run
def run():
    # Configure the app with the title and the icon
    st.set_page_config(page_title="Gemini",page_icon=":star:")
    # Add a header at the start of the page
    st.header(body="Powered by **:rainbow[Google Gemini]**",divider="rainbow")

    # If a session state variable for the message history is not declared, declare it
    if "message_history" not in st.session_state:
        st.session_state.message_history = []
    # Loop through the messsage history to display the message for every rerun
    for message in st.session_state.message_history:
        # Use the corresponding role for each message
        with st.chat_message(message["role"]):
            # If the message is an image, display the image using the appropriate function
            if message["content"] == "image":
                st.image(message["file"])
            # Else if the message is blocked, throw a warning
            elif message["content"] == "blocked":
                st.warning("Inappropriate Prompt Detected.",icon="⚠️")
            # Else, just display the content of the message
            else:
                st.markdown(message["content"])

    # Add a sidebar
    sidebar = st.sidebar
    # Add a caption to the sidebar
    sidebar.caption("Feature Panel") 
    
    # Add a selectbox which contains a list of colours that change the user's text colour
    colours = ("White","Red","Orange","Green","Grey","Blue","Violet","Rainbow")
    colour_choice = sidebar.selectbox(label="Choose a text colour",help="Changes the colour of the user's text in chat",options=colours)

    # Add a divider
    sidebar.divider()

    # Add a file uploader to the sidebar and a button to get the file's information
    pdf_file = sidebar.file_uploader(label="Upload a PDF file",type="pdf",help="Upload a PDF file for Gemini to analyse")
    get_pdf_info = sidebar.button("**Get PDF Info**",type="secondary")

    img_file = sidebar.file_uploader(label="Upload an image file",type=["png","jpg","jpeg"],help="Upload an IMG file for Gemini to analyse")
    get_img_info = sidebar.button("**Get IMG Info**",type="secondary")

    # If a PDF file has been uploaded and the get information button has been pressed, display Gemini's analysis of said file
    if pdf_file and get_pdf_info:
        # Store the PDF file in raw form and create an empty variable to store it's text
        pdf_file_reader  = PdfReader(pdf_file)
        all_data = ""
        # Loop through the pages and add the text to the data variable
        for page in range(pdf_file_reader._get_num_pages()):
            current_page = pdf_file_reader.pages[page]
            all_data += current_page.extract_text()
        
        # Inform the user that a request has been made and store that in the message history
        st.info(f"PDF File: {pdf_file.name}",icon="ℹ️")
        st.session_state.message_history.append({"role":"ℹ️","content":f"**PDF File: {pdf_file.name}**","isBlocked":False})
        # Generate a response that gives details about the uploaded PDF file
        generate_response(f"Give some detailed information about the text below.\n\n{all_data}")
        
    # If an IMG file has been uploaded and the get information button has been pressed, display Gemini's analysis of said file
    if img_file and get_img_info:
        # Inform the user that a request has been made and store that in the message history
        st.info(f"IMG File: {img_file.name}", icon="ℹ️")
        st.session_state.message_history.append({"role":"ℹ️","content":f"**IMG File: {img_file.name}**","isBlocked":False})
        # Convert the img file to a usable format that Gemini can use
        usabled_img_file = PIL.Image.open(img_file)
        # Display the image
        with st.chat_message("user"):
            st.image(image=img_file)
        # Store gemini's analysis of the image in a variable
        img_info = (genai_vision_model.generate_content(usabled_img_file)).text
        # Store the input and response in the message history
        st.session_state.message_history.append({"role":"user","content":"image","isBlocked":False,"file":img_file})
        st.session_state.message_history.append({"role":"ai","content":img_info,"isBlocked":False})
        
        # Display gemini's analysis of the uploaded image
        with st.chat_message("ai"):
                st.markdown(img_info)

    #Add a divider
    sidebar.divider()

    # Add buttons to generate a random prompt, a bot-to-bot conversation and to clear chat history
    random_prompt = sidebar.button(label=":blue[**Generate random prompt**]",type="secondary")
    bot_to_bot = sidebar.button(label=":blue[**Bot-To-Bot Convo**]")
    delete_message_history = sidebar.button(label="**Delete Message History**",type="primary")

    # If the delete button has been pressed, clear the message history
    if delete_message_history:
        
        clear_state()

    # If the bot-to-bot button has been pressed, clear the message history at start to avoid context conflict
    if bot_to_bot:

        st.session_state.message_history.clear()
        # Store the starting message
        second = "greet an ai bot"
        # Loop infinitely and generate a response based on each subsequent response taken as an input
        while True:
          
            first = generate_response(second, role="🔴")
            time.sleep(1)
            second = generate_response(first, role="🔵")
            
    # Store the user input taken from the chat
    prompt_input = st.chat_input("Enter prompt here.")
    
    # If the random prompt button has been pressed, let the user input be a randomly generated prompt taken from Gemini
    if random_prompt:
        with st.spinner("Generating random prompt..."):
            prompt_input = (genai_text_model.generate_content("Generate a random prompt for a chatbot from the user's perspective without surrounding the prompt with quotes.")).text

    # If a message has been entered through the chat, display the prompt with the chosen colour and display the response
    if prompt_input:

        text_colour = colour_choice.lower()

        prompt(prompt_input,text_colour)
        
        generate_response(prompt_input)
               
# If this is the main file, then call the run function 
if __name__ == "__main__":
    run()
