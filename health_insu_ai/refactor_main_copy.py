
from ast import Constant
import time
import streamlit as st
#from streamlit_extras.colored_header import colored_header
from PIL import Image
import base64
#from gtts import gTTS
import os
from audio_recorder_streamlit import audio_recorder
from streamlit_option_menu import option_menu
import google_cloud_speachToText as gcTTS
from constants_p import Constant_m as constant
#from transcription_p import text_audio_transcription_m as tat
from streamlit_float import *
import claims_main as claimsprocessor
import streamlit_authenticator as stauth
import pickle
from helper_p import lanchain_helper_m as lch
import time
from extract_table import CustomPDFParser as cpp
import re
#import streamlit_scrollable_textbox as stx
#icon = Image.open('edu-ai-logo.png')
st.set_page_config(page_title="Insure AI",
                   page_icon=Image.open('./resources/edu-ai-logo.png'),
                   layout="wide",
                   initial_sidebar_state="expanded",
                   )


# --- USER AUTHENTICATION --
names = ["Himanshu Prakash","Admin","Mr. Prakash"]
usernames =["hprakash","admin","hprakash1"]
passwords= []

with open("./auth_p/hashed_pw.pk1","rb") as file:
    passwords = pickle.load(file)
    print("hashed_passwords",passwords)

credentials={"usernames":{}}


for uname,name,pwd in zip(usernames,names,passwords):
   user_dict = {"name":name,"password":pwd} 
   credentials["usernames"].update({uname:user_dict})

# with open("./auth_p/hashed_pw.pk1","rb") as file:
#     hashed_passwords = pickle.load(file)
#     print("hashed_passwords",hashed_passwords)
    

# authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
#     'insureai_cookie_name', 'hpinsureai-3879', cookie_expiry_days=1)
authenticator = stauth.Authenticate(credentials,
     'insureai_cookie_name', 'hpinsureai-3879', cookie_expiry_days=1)

name, authentication_status, username = authenticator.login("sidebar")

if authentication_status == False:
    st.sidebar.error("Username/password is incorrect")
    
if authentication_status == None:
    st.sidebar.warning("Please enter your username and password")

with open('./resources/app.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

with open('./resources/app.js') as f:
    my_js = f.read()

if 'final_md_result' not in st.session_state:
    st.session_state.final_md_result=''
    
if 'upload_files' not in st.session_state:
    st.session_state.upload_files=''

def save_files(document_type,document_name,description,url):
    files=st.session_state.file_upload_widget
    cpp_obj= cpp(document_type,document_name,description,url)
    result = cpp.process_pdf(files.read())
    st.session_state.upload_files=result
    
    return True

def stream_data(input_text):
    for word in input_text.split(" "):
        yield word+" "
        time.sleep(0.02)
        
    
# text to speech using gTTS
# def eduai_text_to_speech(text,lang):
#     # Initialize gTTS with the text to convert
#     speech = gTTS(text=text, lang=lang, slow=False,tld='co.in')
#     # Save the audio file to a temporary file
#     speech_file = 'speech.mp3'
#     speech.save(speech_file)
    
    
if 'summary' not in st.session_state:
    st.session_state.summary = None

if 'language' not in st.session_state:
    st.session_state.language = None
        
def set_state(i):
    st.session_state.stage = i
    

# display audio for text generation          
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

col1,col2 =st.columns(2)
with col1:
    st.image("./resources/edu-ai-logo.png", width=150)
    st.markdown(f"""<a href="https://www.linkedin.com/in/himanshu-prakash-753465a4/" style="font-size: 12px; text-decoration: none">
Follow me @[LinkedIn]</a>""",unsafe_allow_html=True)
with col2:
  pass


if authentication_status:
    def clear_cache():
        keys = list(st.session_state.keys())
        for key in keys:
            st.session_state.pop(key)
            
    col1, col2,col3 = st.sidebar.columns(3)
    with col1:
        authenticator.logout("Logout","main")
    with col2:
     st.button('Clear Cache', on_click=clear_cache)

    st.sidebar.title(f"Welome :red[{name}]")
    planNumber=""
    if username=="hprakash":
        planNumber ="myBlue 2332C"
        original_title = '<p href="https://www.bcbsfl.com/DocumentLibrary/SBC/2023/2332C.pdf" style="font-family:Courier; color:Blue; font-size: 20px;">Plan Number</p>'
        url = "https://www.bcbsfl.com/DocumentLibrary/SBC/2023/2332C.pdf"
        medUrl = "E:/GenAI-Training/CareChoicesMedGuide-pages-pages.pdf"
        claimsUrl = "\\resources\claims.json"
        #st.sidebar.markdown(original_title, unsafe_allow_html=True)
        st.sidebar.markdown(f"Your current plan number is <a href='{url}' style='font-size:12pt'>:red[{planNumber}]</a>" ,unsafe_allow_html=True)
        # st.sidebar.markdown(f"<a href='{medUrl}' style='font-size:12pt'>Medication Guide</a>" ,unsafe_allow_html=True)
        # st.sidebar.markdown(f"<a href='{claimsUrl}' style='font-size:12pt'>Claims Data</a>" ,unsafe_allow_html=True)
        
        # #st.sidebar.markdown(f"Plan Number: [{planNumber}](%s)" % url,unsafe_allow_html=True)
        # st.sidebar.markdown(f"[:red[Medication Guide URL]](%s)" % medUrl)
        # st.sidebar.markdown(f"[:red[Claims Data]](%s)" % claimsUrl)
    
    elif username == "hprakash1":
        planNumber ="BlueOptions-24J01-20S"
        url="https://www.bcbsfl.com/DocumentLibrary/sbc/2024/24J01-20S.pdf"
        medUrl = "file:///E:/GenAI-Training/CareChoicesMedGuide-pages-pages.pdf"
        claimsUrl = "file:///E:/GenAI-Training/PDFServicesSDK-PythonSamples/insure-ai/insure-ai/resources/claims.json"
        st.sidebar.markdown(f"Your current plan number is <a href='{url}' style='font-size:12pt'>:red[{planNumber}]</a>" ,unsafe_allow_html=True)
        # st.sidebar.markdown(f"[:red[Medication Guide URL]](%s)" % medUrl)
        # st.sidebar.markdown(f"[:red[Claims Data]](%s)" % claimsUrl)
        
    
    voiceOn = st.sidebar.toggle('Enable voice')
    
    # collection_type = st.sidebar.select_slider(
    # 'Select your search',
    # options=['benefitsummary', 'medicationguide'])
    #collection_type=st.sidebar.radio('Select your search', options=['benefitsummary', 'medicationguide','claims'])
    #st.sidebar.write('collection_type:', collection_type)
    
    if voiceOn:
        st.sidebar.write('Please ensure that your microphone is enabled for speaking.')
    
    
    with st.sidebar: 
     with st.sidebar.expander("Main Menu"):
            selected = option_menu("", [constant.HOME,constant.UPLOAD_DOCUMENTS,constant.BENEFIT_ASSIST,constant.MED_ASSIST,constant.CLAIMS_ASSIST,constant.SETTINGS], 
            icons=['house','upload','','','','gear'], menu_icon="cast" ,orientation="vertical",
            styles={
                "container": {"padding": "0!important", "background-color": "white"},
                "icon": {"color": "orange", "font-size": "15px"}, 
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                
            }
            )

    #colored_header(label='', description='', color_name='red-10')

    if selected == constant.HOME:
        st.markdown(
        """
        InsureAI will help you to answer any questions related to your :red[Benefits],:red[claims], :red[idcard], :red[payments] etc.
      """
    )
    
    if selected == constant.UPLOAD_DOCUMENTS:
        with st.form(key='sidebar_form'):
            upload_files=st.file_uploader("Upload a pdf file",type=["pdf"],key='file_upload_widget')     

            st.markdown(":red['Below metadata information helps LLM to procide concise answer.']")
            document_type=st.text_input(label="Document Type",placeholder="benefitsummary, medicationguide")
            document_name = st.text_input(label="Document Name",placeholder="myblue-123")
            description = st.text_input(label="description",placeholder="Describe about the document")
            url = st.text_input(label="URL",placeholder="URL of given document if any")
            
            if upload_files:
                st.session_state.upload_files=upload_files
                with st.spinner(text="Processing your document"):
                    save_files(document_type,document_name,description,url)
                    st.success("Files uploaded successfully !!")
                    
            submit_btn = st.form_submit_button("Process upload file")
            
    if selected == constant.BENEFIT_ASSIST:
        user_message=''
        if voiceOn:
            footer_container = st.container()
            with footer_container:
             
             audio_bytes = audio_recorder(text="Click to talk",
                                energy_threshold=0.01,
                                pause_threshold=2.0,
                                neutral_color="#303030",
                                recording_color="#de1212",
                                icon_name="microphone",
                                icon_size="2x",
                                )
             # Float the footer container and provide CSS to target it with
             footer_container.float("bottom: 0rem;")
             
            if audio_bytes:
                if os.path.isfile("./tts_output/transcript.mp3"): 
                    os.remove("./tts_output/transcript.mp3")
                # Write the audio bytes to a file
                with st.spinner("Typing..."):
                    webm_file_path = "temp_audio.mp3"
                    with open(webm_file_path, "wb") as f:
                        f.write(audio_bytes)

                    user_message = tat.speech_to_text(webm_file_path)
            # user_message = 
        else:
            #if collection_type =='benefitsummary':
            placeholder_msg =constant.BENEFIT_INPUT_PLACEHOLDER
                
            # elif collection_type =='claims':
            #     placeholder_msg =constant.CLAIMS_INPUT_PLACEHOLDER
            # else:
            #     placeholder_msg =constant.MEDGUIDE_INPUT_PLACEHOLDER
                
            user_message = st.chat_input(placeholder=placeholder_msg)
        with st.chat_message("AI", avatar="./resources/logo.png"):
            
         #if collection_type =='benefitsummary':
         initial_msg =constant.BENEFIT_INITIAL_BOT_MSG 
         st.write_stream(stream_data(initial_msg))
        #  elif collection_type =='claims':
        #       initial_msg =constant.CLAIMS_INITIAL_BOT_MSG
        #  else:
        #     initial_msg =constant.MEDGUIDE_INITIAL_BOT_MSG
         
         if voiceOn:
          gcTTS.gc_text_to_speech(initial_msg) 
          autoplay_audio("./tts_output/transcript.mp3")                        
         
         st.write(initial_msg)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
                
        def append_state_messages(user_message, bot_message) -> None:
            st.session_state.messages.append({"user_message": user_message, "bot_message": bot_message})

        def restore_history_messages():
            for history_message in st.session_state.messages:
                with st.chat_message("User"):
                    st.write(history_message["user_message"])
                with st.chat_message("AI", avatar="./resources/logo.png"):
                    st.write(history_message["bot_message"])
        if voiceOn and audio_bytes:
            restore_history_messages()
            with st.chat_message("User"):
                    st.write(user_message)
                    
            #if collection_type =='benefitsummary':
            spinner_msg =constant.SPINNER_TEXT_BENEFITSUMMARY 
            # elif collection_type =='claims':
            #     spinner_msg =constant.SPINNER_TEXT_CLAIMS
            # else:
            #     spinner_msg =constant.SPINNER_TEXT_MEDICATIONGUIDE
                 
            gcTTS.gc_text_to_speech(spinner_msg) 
            autoplay_audio("./tts_output/transcript.mp3")       
            with st.spinner(text=spinner_msg):
                collection_type ='benefitbooklet_md'
                response = lch.get_benefit_summary_res_from_hf(user_message,planNumber,collection_type)
                # elif collection_type =='claims':
                #         response = claimsprocessor.process_claims(user_message)    
                # else:
                #         response = lch.get_medguide_res_from_hf(user_message,collection_type)
                autoplay_audio("./tts_output/transcript.mp3")
        
            gcTTS.gc_text_to_speech("I am still reviewing, please wait..") 
            autoplay_audio("./tts_output/transcript.mp3") 
            
            with st.spinner(text="I am still reviewing, please wait.."):
                gcTTS.gc_text_to_speech(response)
                with st.chat_message("AI", avatar="./resources/logo.png"):
                    st.markdown(response)
                append_state_messages(user_message, response)
                    #eduai_text_to_speech(response['answer'],'en')
                    #audio_file = tat.text_to_speech(response)
                    #tat.autoplay_audio(audio_file)
                autoplay_audio("./tts_output/transcript.mp3")
         
        else:
                           
            if user_message:
                restore_history_messages()
                with st.chat_message("User"):
                        st.write(user_message)
                
                # if collection_type =='benefitsummary':
                spinner_msg =constant.SPINNER_TEXT_BENEFITSUMMARY 
                # elif collection_type =='claims':
                #     spinner_msg =constant.SPINNER_TEXT_CLAIMS
                       
                # else:
                #     spinner_msg =constant.SPINNER_TEXT_MEDICATIONGUIDE 
                                
                with st.spinner(text=spinner_msg):
                    collection_type ='benefitbooklet_md'
                    response = lch.get_benefit_summary_res_from_hf(user_message,planNumber,collection_type)
                    answer = response['Answer']
                    answer - re.sub(r'\\',r'\\\\',answer)
                    answer - answer.replace("$","\$")
                    metadata= response['Metadata']                    
                    # elif collection_type =='claims':
                    #     response = claimsprocessor.process_claims(user_message)
                    # else:
                    #     response = lch.get_medguide_res_from_hf(user_message,collection_type)
                        
                with st.chat_message("AI", avatar="./resources/logo.png"):
                        answer+="Thank you, Is thee anything else I can assist you with?"
                        st.write_stream(stream_data(answer))
                        
                        st.markdown("""
                                    <style>
                                    .big-font { font-size:15x !important;
                                    }
                                    </style>
                                    """, unsafe_allow_html=True)
                        st.markdown(f"")
                append_state_messages(user_message, answer)
                
    if selected == constant.MED_ASSIST:
        user_message=''
        if voiceOn:
            footer_container = st.container()
            with footer_container:
             
             audio_bytes = audio_recorder(text="Click to talk",
                                energy_threshold=0.01,
                                pause_threshold=2.0,
                                neutral_color="#303030",
                                recording_color="#de1212",
                                icon_name="microphone",
                                icon_size="2x",
                                )
             # Float the footer container and provide CSS to target it with
             footer_container.float("bottom: 0rem;")
             
             if audio_bytes:
                if os.path.isfile("./tts_output/transcript.mp3"): 
                    os.remove("./tts_output/transcript.mp3")
                # Write the audio bytes to a file
                with st.spinner("Typing..."):
                    webm_file_path = "temp_audio.mp3"
                    with open(webm_file_path, "wb") as f:
                        f.write(audio_bytes)

                    user_message = tat.speech_to_text(webm_file_path)
            # user_message = 
        else:
            # if collection_type =='benefitsummary':
            #     placeholder_msg =constant.BENEFIT_INPUT_PLACEHOLDER
                
            # elif collection_type =='claims':
            #     placeholder_msg =constant.CLAIMS_INPUT_PLACEHOLDER
            # else:
            placeholder_msg =constant.MEDGUIDE_INPUT_PLACEHOLDER
                
            user_message = st.chat_input(placeholder=placeholder_msg)
        with st.chat_message("AI", avatar="./resources/logo.png"):
            
        #  if collection_type =='benefitsummary':
        #     initial_msg =constant.BENEFIT_INITIAL_BOT_MSG 
        #  elif collection_type =='claims':
        #       initial_msg =constant.CLAIMS_INITIAL_BOT_MSG
        #  else:
         initial_msg =constant.MEDGUIDE_INITIAL_BOT_MSG
         
         if voiceOn:
          gcTTS.gc_text_to_speech(initial_msg) 
          autoplay_audio("./tts_output/transcript.mp3")                        
         
         st.write(initial_msg)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
                
        def append_state_messages(user_message, bot_message) -> None:
            st.session_state.messages.append({"user_message": user_message, "bot_message": bot_message})

        def restore_history_messages():
            for history_message in st.session_state.messages:
                with st.chat_message("User"):
                    st.write(history_message["user_message"])
                with st.chat_message("AI", avatar="./resources/logo.png"):
                    st.write(history_message["bot_message"])
        if voiceOn and audio_bytes:
            restore_history_messages()
            with st.chat_message("User"):
                    st.write(user_message)
                    
            # if collection_type =='benefitsummary':
            #     spinner_msg =constant.SPINNER_TEXT_BENEFITSUMMARY 
            # elif collection_type =='claims':
            #     spinner_msg =constant.SPINNER_TEXT_CLAIMS
            # else:
            spinner_msg =constant.SPINNER_TEXT_MEDICATIONGUIDE
                 
            gcTTS.gc_text_to_speech(spinner_msg) 
            autoplay_audio("./tts_output/transcript.mp3")       
            with st.spinner(text=spinner_msg):
                # if collection_type =='benefitsummary':
                #         response = lch.get_benefit_summary_res_from_hf(user_message,planNumber,collection_type)
                # elif collection_type =='claims':
                #         response = claimsprocessor.process_claims(user_message)    
                # else:
                collection_type='medicationguide'
                response = lch.get_medguide_res_from_hf(user_message,collection_type)
                autoplay_audio("./tts_output/transcript.mp3")
        
            gcTTS.gc_text_to_speech("I am still reviewing, please wait..") 
            autoplay_audio("./tts_output/transcript.mp3") 
            
            with st.spinner(text="I am still reviewing, please wait.."):
                gcTTS.gc_text_to_speech(response)
                with st.chat_message("AI", avatar="./resources/logo.png"):
                    st.markdown(response)
                append_state_messages(user_message, response)
                    #eduai_text_to_speech(response['answer'],'en')
                    #audio_file = tat.text_to_speech(response)
                    #tat.autoplay_audio(audio_file)
                autoplay_audio("./tts_output/transcript.mp3")
         
        else:
                           
            if user_message:
                restore_history_messages()
                with st.chat_message("User"):
                        st.write(user_message)
                
                # if collection_type =='benefitsummary':
                #     spinner_msg =constant.SPINNER_TEXT_BENEFITSUMMARY 
                # elif collection_type =='claims':
                #     spinner_msg =constant.SPINNER_TEXT_CLAIMS
                       
                # else:
                spinner_msg =constant.SPINNER_TEXT_MEDICATIONGUIDE 
                                
                with st.spinner(text=spinner_msg):
                    # if collection_type =='benefitsummary':
                    #     response = lch.get_benefit_summary_res_from_hf(user_message,planNumber,collection_type)
                    # elif collection_type =='claims':
                    #     response = claimsprocessor.process_claims(user_message)
                    # else:
                    collection_type='medicationguide'
                    response = lch.get_medguide_res_from_hf(user_message,collection_type)
                        
                with st.chat_message("AI", avatar="./resources/logo.png"):
                        st.markdown(response)
                append_state_messages(user_message, response)
                
    if selected == constant.CLAIMS_ASSIST:
        user_message=''
        if voiceOn:
            footer_container = st.container()
            with footer_container:
             
             audio_bytes = audio_recorder(text="Click to talk",
                                energy_threshold=0.01,
                                pause_threshold=2.0,
                                neutral_color="#303030",
                                recording_color="#de1212",
                                icon_name="microphone",
                                icon_size="2x",
                                )
             # Float the footer container and provide CSS to target it with
             footer_container.float("bottom: 0rem;")
             
             if audio_bytes:
                if os.path.isfile("./tts_output/transcript.mp3"): 
                    os.remove("./tts_output/transcript.mp3")
                # Write the audio bytes to a file
                with st.spinner("Typing..."):
                    webm_file_path = "temp_audio.mp3"
                    with open(webm_file_path, "wb") as f:
                        f.write(audio_bytes)

                    user_message = tat.speech_to_text(webm_file_path)
            # user_message = 
        else:
            # if collection_type =='benefitsummary':
            #     placeholder_msg =constant.BENEFIT_INPUT_PLACEHOLDER
                
            #elif collection_type =='claims':
            placeholder_msg =constant.CLAIMS_INPUT_PLACEHOLDER
            # # else:
            # placeholder_msg =constant.MEDGUIDE_INPUT_PLACEHOLDER
                
            user_message = st.chat_input(placeholder=placeholder_msg)
        with st.chat_message("AI", avatar="./resources/logo.png"):
            
        #  if collection_type =='benefitsummary':
        #     initial_msg =constant.BENEFIT_INITIAL_BOT_MSG 
        #  elif collection_type =='claims':
         initial_msg =constant.CLAIMS_INITIAL_BOT_MSG
        #  else:
        #  initial_msg =constant.MEDGUIDE_INITIAL_BOT_MSG
         
         if voiceOn:
          gcTTS.gc_text_to_speech(initial_msg) 
          autoplay_audio("./tts_output/transcript.mp3")                        
         
         st.write(initial_msg)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
                
        def append_state_messages(user_message, bot_message) -> None:
            st.session_state.messages.append({"user_message": user_message, "bot_message": bot_message})

        def restore_history_messages():
            for history_message in st.session_state.messages:
                with st.chat_message("User"):
                    st.write(history_message["user_message"])
                with st.chat_message("AI", avatar="./resources/logo.png"):
                    st.write(history_message["bot_message"])
        if voiceOn and audio_bytes:
            restore_history_messages()
            with st.chat_message("User"):
                    st.write(user_message)
                    
            # if collection_type =='benefitsummary':
            #     spinner_msg =constant.SPINNER_TEXT_BENEFITSUMMARY 
            # elif collection_type =='claims':
            spinner_msg =constant.SPINNER_TEXT_CLAIMS
            # else:
            #spinner_msg =constant.SPINNER_TEXT_MEDICATIONGUIDE
                 
            gcTTS.gc_text_to_speech(spinner_msg) 
            autoplay_audio("./tts_output/transcript.mp3")       
            with st.spinner(text=spinner_msg):
                # if collection_type =='benefitsummary':
                #         response = lch.get_benefit_summary_res_from_hf(user_message,planNumber,collection_type)
                collection_type ='claims'
                response = claimsprocessor.process_claims(user_message)    
                # else:
                # collection_type='medicationguide'
                # response = lch.get_medguide_res_from_hf(user_message,collection_type)
                autoplay_audio("./tts_output/transcript.mp3")
        
            gcTTS.gc_text_to_speech("I am still reviewing, please wait..") 
            autoplay_audio("./tts_output/transcript.mp3") 
            
            with st.spinner(text="I am still reviewing, please wait.."):
                gcTTS.gc_text_to_speech(response)
                with st.chat_message("AI", avatar="./resources/logo.png"):
                    st.markdown(response)
                append_state_messages(user_message, response)
                    #eduai_text_to_speech(response['answer'],'en')
                    #audio_file = tat.text_to_speech(response)
                    #tat.autoplay_audio(audio_file)
                autoplay_audio("./tts_output/transcript.mp3")
         
        else:
                           
            if user_message:
                restore_history_messages()
                with st.chat_message("User"):
                        st.write(user_message)
                
                # if collection_type =='benefitsummary':
                #     spinner_msg =constant.SPINNER_TEXT_BENEFITSUMMARY 
                # elif collection_type =='claims':
                spinner_msg =constant.SPINNER_TEXT_CLAIMS
                       
                # else:
                #spinner_msg =constant.SPINNER_TEXT_MEDICATIONGUIDE 
                                
                with st.spinner(text=spinner_msg):
                    # if collection_type =='benefitsummary':
                    #     response = lch.get_benefit_summary_res_from_hf(user_message,planNumber,collection_type)
                    collection_type ='claims'
                    response = claimsprocessor.process_claims(user_message)
                    # else:
                    # collection_type='medicationguide'
                    # response = lch.get_medguide_res_from_hf(user_message,collection_type)
                        
                with st.chat_message("AI", avatar="./resources/logo.png"):
                        st.markdown(response)
                append_state_messages(user_message, response)
                
        

            


        

