#from flask import jsonify
#from matplotlib.font_manager import json_dump
from numpy import empty
import streamlit as st 
from langchain.llms import OpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.llms import OpenAI
from langchain_community.llms import HuggingFaceEndpoint
import os
from langsmith import Client
from dotenv import load_dotenv
import requests
import json
from langchain.text_splitter import TokenTextSplitter
from langchain_community.document_loaders import DataFrameLoader
import pandas as pd
from langchain.chat_models import ChatOpenAI

from claims_processor_m import extract_data_kor as extract_data, filter_claims_data_m as filter_data
load_dotenv()
# from langchain_community.document_loaders.pebblo import PebbloSafeLoader
text_splitter = TokenTextSplitter(chunk_size=512,chunk_overlap=103)


def process_claims_chunk(question,df):

    print(df)
    new_list=split_text(df)
    df_new = pd.DataFrame(new_list, columns=['content'])
    print('df_new',df_new)
    #dataset = dataset.from_pandas(df_new)
    loader = DataFrameLoader(df_new, page_content_column = 'content')
    docs = loader.load()
   
    if docs is not empty:
       
        context=str(docs)
        print('docs',str(docs))
            
        template = """  
             Your are a Florida blue insurence company agent whose job is to Write a concise summary. \
      
            ONLY if below claims data contain the answer to the question then explain the answer in bullet points which covers the key points. If the member is asking last or latest claims then return lastest claims based on service date.\
            ONLY If below claims data does not contain the answer to the question then return text "Currently, I am equipped to address inquiries related to claims exclusively. I couldn’t locate any relevant information in your your claims data.", don't try to make up an answer and also, DO NOT answer from context.\
            
            
            claims data: {context}
            question: {question} 
           
           Create pie chart by using The claim charge, Florida Blue paid and The total member responsibility.\    
           Always, end with thank you and ask user if they have any further question related to their claims. \ns
           Always replace  context', if it is contain in answer with, ' claims data'.
            """
        URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        
        #mistral 7b paid
        #URL = "https://ene9aelpje3n3xtu.us-east-1.aws.endpoints.huggingface.cloud"
        #URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        # Llama-2-7b
        #URL = "https://ydd0y5m47xxk21ns.us-east-1.aws.endpoints.huggingface.cloud"
        #Llama-2-13b
        #URL = "https://nxfo8r0q3jggjats.us-east4.gcp.endpoints.huggingface.cloud"
        # llama-2-70b
        #URL = "https://s6bsx8e9icxxd0wi.us-east-1.aws.endpoints.huggingface.cloud" 
        endpoint_url = (URL)
        llm = HuggingFaceEndpoint(
                task="text-generation",
                endpoint_url=endpoint_url,
                temperature=1,
                huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
                model_kwargs={},
        )
        
        #    llm = ChatOpenAI(
        #         model_name="gpt-3.5-turbo",
        #         temperature=1,
        #         max_tokens=2000,
        #         model_kwargs = {
        #             'frequency_penalty':0,
        #             'presence_penalty':0,
        #             'top_p':1.0
        #         }
        #     )
            
        prompt_template_name = PromptTemplate(
            input_variables = ['context','question'],
            template= template
        )
        name_chain = LLMChain(llm=llm, prompt=prompt_template_name)
        response = name_chain({'context':context,'question': question})
        
        print(response)
    else:
     response="It appears that either the question is unrelated to claims or lacks sufficient context for searching within your claims"
   
    return response




def split_text(df):
    new_list=[]
    
    df = df.reset_index(drop=True)
    
    num_col=df.shape[1]
    for i in range(len(df.index)):
        text=""
        for col in range(num_col):
           
            text += str(df.columns.values[col])+':'+str(df[df.columns.values[col]][i])+' '
            split_text = text_splitter.split_text(text)
        for j in range(len(split_text)):
            new_list.append([split_text[j]])
           
    return new_list



def process_claims(question):
    
    file_path='./resources/claims.json'
    print('file_path',file_path)
    with open(file_path) as data_file:    
        data = json.load(data_file)
    
    #print('data',data)
    filter_query=extract_data.extract_userinput_data(question)
    if filter_query is not None and len(filter_query) >0:
        print('filter_query',len(filter_query))
        datachunk=filter_data.filter_data(filter_query,data) 
        finalResponse = process_claims_chunk(question,datachunk)
        #print('finalResponse',finalResponse.text)
        #json_object = json.dumps(finalResponse, indent = 4) 
        json_obj = json.dumps(finalResponse,indent=3);
        resp_data = json.loads(json_obj)
        
        result=resp_data.get("text")
        # #result = json.dumps(finalResponse)
        result=result.replace("$", "\$")
        result=result.replace("Answer:","")
        print('result',result)
        return result
    else:
        return "It appears that either the question is unrelated to claims or lacks sufficient context for searching within your claims"
#input = "I’d like to know the status of my pharmacy claim for my daughter" 
   
# question = "what is my last Medical Claims status?"
# process_claims(question)