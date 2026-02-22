from ast import arg
from langchain_text_splitters import MarkdownTextSplitter, TextSplitter
import pandas as pd
import pymupdf
import os
import pandas as pd
from pathlib import Path
import pickle
import asyncio
import sys
import json
import pymupdf4llm

class CustomPDFParseNChunk:
    
    def __init__(self,**kwargs):

        self.document_type=kwargs.get("doc_type")
        self.document_name=kwargs.get("doc_name")
        self.description=kwargs.get("doc_description")
        self.url=kwargs.get("doc_link")
        self.output_format=kwargs.get("output_format")
        self.chunk_size=kwargs.get("chunk_size")
        self.chunk_overlaps=kwargs.get("chunk_overlap")
        self.layout_options=kwargs.get("pdf_layout").get("layout_options")
        self.tabular_data_format=kwargs.get("pdf_layout").get("tabular_data_format")
        self.template_format=kwargs.get("pdf_layout").get("template_format")
        
        self.root_path = f'./resources/pdfextract_output/{self.document_type}/{self.document_name}'
        list = ['md', 'images', 'json']
        try:
            for items in list:
                path=Path(f'{self.root_path}/{items}')
                path.mkdir(parents=True,exist_ok=True)
        except Exception as e:
            print(f'Something went wrong creating folder {e}')
    
    
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
        
        json_list=[]
        for page_number in range(doc.page_count):
            page = doc[page_number]
            tabs = page.find_tables()
            
            page_metadata={}
            page_table_dict={}
            page_table_text_dict={}
            page_text_dict={}
            
            json_dict={}
            
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
                       
                    if table_json:
                        json_dict['metadata']=page_metadata
                        json_output=json.loads(table_json)
                        json_dict.update(json_output)
                        #json_dict['page_content']=table_json
                        json_list.append(json_dict)
                        #json_list.append(json_output)
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
                    
                    json_dict['metadata']=page_metadata
                    json_dict['page_content']=page_text
                    json_list.append(json_dict)
        doc.close()
       
        # final_json =json.load(table_json)
        # final_json.ap
        return markdown_list,json_list      

    
    def process_pdf(self,pdfFilePath):
        """Start: process_pdf function """
        try:
          print(f'Size of pdf :{len(pdfFilePath)}')
            #self.write_bytestream_to_pickle(pdfFilePath)
          if 'tabular_data' in self.layout_options:
            if self.tabular_data_format == 'table_to_text' and self.template_format:
              document_list,json_list=self.extract_table_text_from_pdf(pdfFilePath, self.template_format)
            else:
              document_list,json_list=self.extract_table_text_from_pdf(pdfFilePath)  
            
            self.convert_pdf_page_to_image(pdfFilePath)
            
            splitter = MarkdownTextSplitter(chunk_size=2000,chunk_overlap=200)
            
            list_docs=[]
            for page in document_list:
                docs = splitter.create_documents([page['text']])
                for doc in docs:
                    doc.metadata = page['metadata']
                    list_docs.append(doc)
          else:
               doc = pymupdf.open(stream=pdfFilePath,filetype="pdf")
               md_text = pymupdf4llm.to_markdown(doc,page_chunks=True)
               md_list=[] 
               #print(md_text)       
               for page in md_text:
                    md_json_output={} 
                    page_metadata={}
                    page_metadata['page_number'] = page.get("metadata").get("page")
                    md_json_output.update(page_metadata)
                    text=page.get("text")
                    print(f'text : {text}')
                    md_json_output['text']=text
                    print(f'metadata : {page.get("metadata").get("page")}')
                    
                    md_list.append(md_json_output)
                    #md_list.append(text)   
               
                
        except OSError as e:
            print(f"Error : {e}")
        print('output_format',self.output_format)
        
        if self.output_format == 'Json':
           print(f'Json List: {json_list}')
           return json_list
       
        elif self.output_format == 'Markdown':
         return document_list
     
        if self.output_format == 'plain_text':
           print(f'md_text: {md_text}')
           return md_list
       
        else:          
         return list_docs
    
    def get_pdf_bytestream(self,file_path):
        with open(file_path,'rb') as f:
            return f.read() 

def _execute_(pdfFilePath,**kwargs):
    obj = CustomPDFParseNChunk(**kwargs)
    #get_pdf_bytestream= obj.get_pdf_bytestream(link)
    result=obj.process_pdf(pdfFilePath)
    return result
    
if __name__ == "__main__":
    
    if len(sys.argv) > 2:
        document_type = sys.argv[1]
        document_name = sys.argv[2]
        description = sys.argv[3]
        link = sys.argv[4]
    obj = CustomPDFParseNChunk(document_type,document_name,description,link,
                               format="chunk",chunk_size=2000,chunk_overlaps=200)
    get_pdf_bytestream= obj.get_pdf_bytestream(link)
    obj.process_pdf(get_pdf_bytestream)
    
    
#     {
#   "doc_type": "",
#   "doc_name": "",
#   "doc_description": "",
#   "doc_link": "",
#   "output_format": "",
#   "chunk_size": "",
#   "chunk_overlap": "",
#   "pdf_layout": {
#     "layout_options": [
#       "plain_text",
#       "tabular_data",
#       "images"
#     ],
#     "tabular_data_format": "table_to_text|markdown",
#     "template_format": "[column1] is [column2]."
#   }
# }

