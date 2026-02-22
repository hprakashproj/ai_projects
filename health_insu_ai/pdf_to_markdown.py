import pymupdf4llm
from langchain_text_splitters import MarkdownTextSplitter
import fitz  # PyMuPDF's new name
from dbprocessor_m import upsert_pgvector_db,pgvector_db_retriever
import os
from pathlib import Path

def extract_images(pdf_path):
    
   try: 
    base_path=os.path.splitext(os.path.basename(pdf_path))[0]  
    print('base_path',base_path)
    
    directory = Path(base_path+'/images')
    directory.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)

    for page_num in range(doc.page_count):
        page = doc[page_num]
        pix  = page.get_pixmap()
    # Save the image
        pix.save(f"{base_path}/images/page_image_{page_num + 1}.png") 
  
   except OSError as e:
    print(f"Error: {e}")

def markdown_chunks(pdf_path,plannumber):

    base_path=os.path.splitext(os.path.basename(pdf_path))[0]  
    split_by_page_md= pymupdf4llm.to_markdown(pdf_path,page_chunks=True)
    extract_images(pdf_path)
    
    md_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)

    
    document_list=[]

    for page in split_by_page_md:
        page_metadata={}
        page_num=page['metadata']['page']
        page_metadata['page_number']=page_num
        page_metadata['plannumber']=plannumber
        page_metadata['pdf_url']=pdf_path
        page_metadata['page_image_path']=f"{base_path}/images/page_image_{page_num}.png"
        
        docs = md_splitter.create_documents([page['text']])
        
        for doc in docs:
            print('page_metadata',page_metadata)
            doc.metadata =page_metadata
            document_list.append(doc)
     
    print('document_list',document_list)    
    return document_list
#db = upsert_pgvector_db(page_content_list,'')

def insert_update_pgvector_db(pdf_path,plannumber):
    
    collection_name=f"benefit_summary_{plannumber}"
    
    docs=markdown_chunks(pdf_path,plannumber)
    db = upsert_pgvector_db(docs,collection_name)
    
    return db

if __name__ == "__main__":
    
    collection_name=f"benefit_summary_myBlue 2332C"
    
    #db=insert_update_pgvector_db('./resources/benefitsummary.pdf','myBlue 2332C')
    
    db_retriever= pgvector_db_retriever(collection_name)
    question = "what is my deductible?"
    docs =db_retriever.similarity_search(question, k=3,filter={'plannumber':'myBlue 2332C'})
   #print('docs',docs)
    #retriever=db_retriever.as_retriever(search_kwargs={'k': 3,'score_threshold':0.9,'filter':{'plannumber': 'myBlue 2332C'}})
    
    print(docs)