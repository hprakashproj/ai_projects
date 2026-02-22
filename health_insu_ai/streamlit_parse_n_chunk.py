

import time
import streamlit as st
from streamlit_option_menu import option_menu
import CustomPDFParseNChunk as parsenchunk
from CustomPDFParseNChunk import CustomPDFParseNChunk as cpp
import re

kwargs = { "doc_type": "", 
          "doc_name": "", 
          "doc_description": "", 
          "doc_link": "", 
          "output_format": "", 
          "chunk_size": "", 
          "chunk_overlap": "", 
          "pdf_layout": { "layout_options": [], 
          "tabular_data_format": "", 
          "template_format": "" 
          }
          }

if 'final_md_result' not in st.session_state:
    st.session_state.final_md_result=''
    
if 'upload_files' not in st.session_state:
    st.session_state.upload_files=''

if 'final_chunk' not in st.session_state:
    st.session_state.final_chunk=''

class customClass:
    
    def save_files(self,document_type,document_name,description,url,
                   chunkFormat,chunk_size,chunk_overlaps,layout_options,tabular_output_format,template):
        files=st.session_state.file_upload_widget
        print(files.size)
        print(f'layout_options: {layout_options}')
        # Set values in the kwargs dictionary 
        kwargs["doc_type"] = document_type 
        kwargs["doc_name"] = document_name 
        kwargs["doc_description"] = description 
        kwargs["doc_link"] = url 
        kwargs["output_format"] = chunkFormat
        kwargs["chunk_size"] = chunk_size 
        kwargs["chunk_overlap"] = chunk_overlaps 
        kwargs["pdf_layout"]["layout_options"] = layout_options #["plain_text", "tabular_data"] 
        kwargs["pdf_layout"]["tabular_output_format"] = tabular_output_format #"markwargskdown" 
        kwargs["pdf_layout"]["template_format"] = template #"[column1] corresponds to [column2]."
        
        print(document_type,document_name,description,url,chunkFormat,chunk_size,chunk_overlaps)
        cpp_obj= cpp(**kwargs)
        result = parsenchunk._execute_(files.read(),**kwargs)
        
        st.session_state.final_chunk=result
        
        return True

with st.sidebar: 
    with st.sidebar.expander("Main Menu"):
        selected = option_menu("", ['UPLOAD_DOCUMENTS',], 
        icons=['upload'], menu_icon="cast" ,orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "white"},
            "icon": {"color": "orange", "font-size": "15px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            
        }
        )

    #colored_header(label='', description='', color_name='red-10')

  
    if selected == 'UPLOAD_DOCUMENTS':
        with st.form(key='sidebar_form'):
            upload_files=st.file_uploader("Upload a pdf file",type=["pdf"],key='file_upload_widget')     

            with st.expander("PDF Layout"): 
                layout_options = []
                plain_text = st.checkbox('Plain Text') 
                if plain_text:
                    layout_options.append(plain_text)
                tabular_data = st.checkbox('Tabular Data')
                if tabular_data:
                    layout_options.append(tabular_data)
                    
                image = st.checkbox('Image(s)')
                if image:
                    layout_options.append(image)
                    
            tabular_output_format='Markdown'        
           
            options = ['--Select--', 'table_to_text', 'Markdown']
            tabular_output_format = option = st.selectbox(
                                        'Tabular data output format',
                                        options)
            
            template_format=''    
            #if tabular_output_format=='table_to_text':
            template_format = st.text_input(label="Table Template",placeholder="[column1] has [column2] value.")   
             
            st.markdown(":red['Below metadata information helps LLM to provide concise answer.']")
            
                
            document_type=st.text_input(label="Document Type",placeholder="benefitsummary, medicationguide")
            document_name = st.text_input(label="Document Name",placeholder="myblue-123")
            description = st.text_input(label="description",placeholder="Describe about the document")
            url = st.text_input(label="URL",placeholder="URL of given document if any")
            options = ['Select an option', 'Chunk', 'Markdown', 'Json','plain_text']
            output_format = option = st.selectbox(
                                        'Select chunk output format',
                                        options)
            chunk_size=0
            chunk_overlaps=0
            if output_format == 'Chunk':
                chunk_size = st.text_input(label="Chunk Size",placeholder="2000")
                chunk_overlaps = st.text_input(label="Chunk Overlaps",placeholder="200")
            
            if upload_files:
                st.session_state.upload_files=upload_files
                with st.spinner(text="Processing your document"):
                    cc= customClass()
                    cc.save_files(document_type,document_name,description,url,
                                  output_format,chunk_size,chunk_overlaps,layout_options,tabular_output_format,template_format)
                    st.success("Files uploaded successfully !!")
                    
            submit_btn = st.form_submit_button("Process upload file")

st.markdown('Display output')            
st.write(st.session_state.final_chunk)   
        

            


        

