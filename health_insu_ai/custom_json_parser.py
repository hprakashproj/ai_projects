from http.client import FORBIDDEN
import json
from typing import Annotated, List
from pydantic import BaseModel, Extra, Field

from langchain_core.output_parsers import JsonOutputParser

class Metadata(BaseModel):
    class Config:
        extra = Extra.forbid
    page_number: str = Field(description="Include page_number from context \
                             metadata only if answer is from give context")
    image_path: str = Field(description="Include image_path from context \
                             metadata only if answer is from give context")
    url: str = Field(description="Include url from context \
                             metadata only if answer is from give context")

class LLMResponse(BaseModel):
    class Config:
        extra = Extra.forbid
    Answer: str = Field(description="Provide concise answer from the given context. \
                            Please make sure to include all the information from the context. \
                            If the answer is not from context then just say \
                                'Sorry I could not find the answer to your question. It might help if you ask in different way.'")
    Metadata:Metadata
    
if __name__ =="__main__":
    print(json.dumps(LLMResponse.model_json_schema(), indent=2))