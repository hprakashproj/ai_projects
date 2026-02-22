from ast import arg
from langchain_text_splitters import MarkdownTextSplitter, TextSplitter
import pandas as pd
import pymupdf
import os
import pandas as pd
from pathlib import Path
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
import pickle
import asyncio
import sys
from vectorstores import PGVector
from dotenv import load_dotenv, find_dotenv
from langchain_community.vectorstores.pgvector import DistanceStrategy

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_ = load_dotenv(find_dotenv())

embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key= os.environ['HUGGINGFACEHUB_API_TOKEN'], model_name="BAAI/bge-base-en-v1.5"
)
  # Initialize Embeddings
# embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    

def get_pgvector_connection():
   # Build the PGVector Connection String from params
# Found in the credential cheat-sheet or "Connection Info" in the Timescale console
# In terminal, run: export VAR_NAME=value for each of the values below
   host= os.environ['LOCAL_HOST']
   port= os.environ['LOCAL_PORT']
   user= os.environ['LOCAL_USER']
   password= os.environ['LOCAL_PASSWORD']
   dbname= os.environ['LOCAL_DBNAME']
   dbschema=os.environ['LOCAL_DB_SCHEMA']
   # We use postgresql rather than postgres in the conn string since LangChain uses sqlalchemy under the hood
   # You can remove the ?sslmode=require if you have a local PostgreSQL instance running without SSL
   CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"

   return CONNECTION_STRING

class CustomPDFParser:
    
    def __init__(self,document_type,document_name,description,url):

        self.document_type=document_type
        self.document_name=document_name
        self.description=description
        self.url=url
        
        self.root_path = f'./resources/pdfextract_output/{document_type}/{document_name}'
        list = ['md', 'images', 'json']
        try:
            for items in list:
                path=Path(f'{self.root_path}/{items}')
                path.mkdir(parents=True,exist_ok=True)
        except Exception as e:
            print(f'Something went wrong creating folder {e}')
    
    def apgvector_db_retriever(self,collection_name):
        store = PGVector(
        collection_name=collection_name,
        connection=get_pgvector_connection(),
        embeddings=embeddings,
        distance_strategy = DistanceStrategy.COSINE,
        use_jsonb=True,
        async_mode=True
    
    )
    
    def write_bytestream_to_pickle(self,bytestream):
        """Writes a bytestream to a pickle file."""
        with open(f'{self.root_path}/{self.document_type}-{self.document_name}.pk1', 'wb') as f:
            pickle.dump(bytestream, f)
        
        
    def convert_pdf_page_to_image(self,doc_byte_stream):
        try:
            doc = pymupdf.open(stream=doc_byte_stream,filetype='pdf')
            for page in doc:
                pix = page.get_pixmap()
                pix.save(f'{self.root_path}/images/page-{page.number}.png')
                
            doc.close()
        except Exception as e:
            print(f'Failed to crate create image of pdf page {e}')
        
            
   
            
    async def execute_db(self,list_docs,collection_name):
        print(f"Execute Database: Docs length {len(list_docs)}")
        try:
            
            db= self.apgvector_db_retriever(collection_name)
            
            async def embed_group(docs):
                await db.aadd_documents(docs)
            
            n =int(len(list_docs) /10 )
            doc_groups = [list_docs[i:i+n] for i in range(0, len(list_docs), n)]
            
            tasks = [embed_group(group) for group in doc_groups]
            await asyncio.gather(*tasks)
            print("Documents added to pgvector successfully !!")
            
        except Exception as e:
            print(f'Error in inserting data in PG Vector DB {e}')
            
       
        
        

    def generate_markdown(self,data,pageindex):
        try:
            cleaned_data=[]
            for row in data:
                cleaned_row = [str(value).replace('\n',' ') for value in row]
                cleaned_data.append(cleaned_row)
                
            #create a dataframe
            df = pd.DataFrame(cleaned_data[1:],columns=cleaned_data[0])
            df_json = df.copy(deep=True)
            df.columns = df.columns.str.strip()
            # convert to markdown table
            
            markdown_table = df.to_markdown(index=False)
            
            df_json.reset_index(drop=True, inplace=True)
            json_table= df_json.to_json(index=False,indent=1,orient="split")
            # write into file
            with open(f'{self.root_path}/md/page-{pageindex}.md', "w", encoding='utf-8') as f:
                f.write(markdown_table)
            
            with open(f'{self.root_path}/json/page-{pageindex}.json', "w", encoding='utf-8') as f:
                f.write(json_table)
                
            f.close()
            
            return markdown_table,json_table

        except Exception as e:
          print(f"Exception from generate_markdown : {e}")


    def extract_table_text_from_pdf(self,pdfFilePath):
        print(f"**Start: Inside extract_table_text_from_pdf Function **")
        doc = pymupdf.open(stream=pdfFilePath,filetype="pdf")
        #get page number
        num_pages = doc.page_count
        print(f"page number : {num_pages}")
        # get all tables from pdf
        markdown_list=[]
        for page_number in range(doc.page_count):
            page = doc[page_number]
            tabs = page.find_tables()
            
            page_metadata={}
            page_table_dict={}
            page_table_text_dict={}
            page_text_dict={}
            
            page_metadata['page_number']=page_number+1
            page_metadata['image_path']=f'{self.root_path}/images/page-{page_number}.png'
            page_metadata['url']=self.url
            page_metadata['document_name']=self.document_name
            page_metadata['description']=self.description
            
            if tabs.tables:
                for tab in tabs:
                    table_md,table_json=self.generate_markdown(tab.extract(),page_number)
                    if table_md:
                        page_table_dict['text']=table_md
                        page_table_dict['metadata']=page_metadata
                        markdown_list.append(page_table_dict)
                # erase all table text to get plain text from page 
                page.add_redact_annot(tab.bbox) # wrap table in a redaction annotation
                page.apply_redactions() # erage all table text
                
                # get text from page
                table_text = page.get_text()
                #write into file 
                
                if table_text:
                    
                    with open(f'{self.root_path}/md/page-text-{page_number}.md', "w", encoding='utf-8') as f:
                        f.write(table_text)
                    f.close()
                    page_table_text_dict['text']=table_text   
                    page_table_text_dict['metadata']=page_metadata
                    markdown_list.append(page_table_text_dict)
            else:
                page_text = page.get_text()
                with open(f'{self.root_path}/md/page-text-{page_number}.md', "w", encoding='utf-8') as f:
                    f.write(page_text)
                f.close()
       
                if page_text:
                    page_text_dict['text']=page_text
                    page_text_dict['metadata']=page_metadata
                    markdown_list.append(page_text_dict)
        doc.close()
       
        return markdown_list      

    
    def process_pdf(self,pdfFilePath):
        """Start: process_pdf function """
        try:
            print(f'Size of pdf :{len(pdfFilePath)}')
            self.write_bytestream_to_pickle(pdfFilePath)
            document_list=self.extract_table_text_from_pdf(pdfFilePath)
            self.convert_pdf_page_to_image(pdfFilePath)
            
            splitter = MarkdownTextSplitter(chunk_size=2000,chunk_overlap=200)
            
            list_docs=[]
            for page in document_list:
                docs = splitter.create_documents([page['text']])
                for doc in docs:
                    doc.metadata = page['metadata']
                    list_docs.append(doc)
                    
            asyncio.run(self.execute_db(list_docs,self.document_type+'-'+self.document_name))
            #db= upsert_pgvector_db(list_docs,"benefitsummary-24J01-17")
            print(f'Database Execution Successfully **')
        
        except OSError as e:
            print(f"Error : {e}")

    
    def get_pdf_bytestream(self,file_path):
        with open(file_path,'rb') as f:
            return f.read() 


if __name__ == "__main__":
    
    if len(sys.argv) > 2:
        document_type = sys.argv[1]
        document_name = sys.argv[2]
        description = sys.argv[3]
        link = sys.argv[4]
    obj = CustomPDFParser(document_type,document_name,description,link)
    get_pdf_bytestream= obj.get_pdf_bytestream(link)
    obj.process_pdf(get_pdf_bytestream)
    