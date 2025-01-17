from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.llms.ctransformers import CTransformers
from langchain.chains import RetrievalQA
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from config import *
import chainlit as cl
import requests

class SAIGE:

    # URL of the file to be downloaded
    url = "https://upnow-prod.ff45e40d1a1c8f7e7de4e976d0c9e555.r2.cloudflarestorage.com/RULi7mYWhJNrGC3FKqWvjw9IfJb2/11a4e468-c569-431a-ab24-d4a426ae5d72?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=cdd12e35bbd220303957dc5603a4cc8e%2F20231114%2Fauto%2Fs3%2Faws4_request&X-Amz-Date=20231114T093118Z&X-Amz-Expires=43200&X-Amz-Signature=5661011d9e24a030b0858606fff8320e896935fb902eb01da5f72635b991ed24&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3D%22llama-2-7b-chat.ggmlv3.q8_0.bin%22"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        file_name = "llama-2-7b-chat.ggmlv3.q8_0.bin"
    # Save the file
        with open(file_name, 'wb') as file:
            file.write(response.content)
            print(f"File downloaded successfully as {file_name}")
    else:
        print(f"Error: Unable to download the file. Status code: {response.status_code}")

    

    def __init__(self) -> None:

        self.prompt_template = PROMPT_TEMPLATE
        self.input_variables = INP_VARS
        self.chain_type = CHAIN_TYPE
        self.search_kwargs = SEARCH_KWARGS
        self.embedder = EMBEDDER
        self.model_ckpt = MODEL_CKPT
        self.model_type = MODEL_TYPE
        self.max_new_tokens = MAX_NEW_TOKENS
        self.temperature = TEMPERATURE
        self.top_p = TOP_P
        self.top_k = TOP_K
        self.do_sample = DO_SAMPLE
        self.repetition_penalty = REPETITION_PENALTY

        self._setup_utils()

    def _prompt_util(self):
        self.prompt = PromptTemplate.from_template(template=PROMPT_TEMPLATE)

    def _llm_util(self):
        self.llm = CTransformers(
            model=self.model_ckpt,
            model_type=self.model_type,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            do_sample=self.do_sample,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty
        )
    
    def _qa_chain_util(self) -> None:
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.db.as_retriever(search_kwargs=self.search_kwargs),
            chain_type=self.chain_type,
            chain_type_kwargs={"prompt" : self.prompt},
            return_source_documents=True
        )
        # self.chain = (
        #     {"context" : self._retriever, "question" : RunnablePassthrough()}
        #     | self.prompt
        #     | self.llm
        #     | StrOutputParser()
        #     )
    

    
    def _retriever(self, query: str):
        return self.db.as_retriever(
            search_kwargs=SEARCH_KWARGS
        ).invoke(query)


    def _setup_utils(self):

        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedder,
            model_kwargs={"device" : "cpu"}
        )
        self.db = FAISS.load_local(
            folder_path=DB_PATH,
            embeddings=self.embeddings
        )

        self._prompt_util()
        self._llm_util()
        self._qa_chain_util()

    
    def query(self, query: str) -> str:
        response = self.chain({"query" : query})
        return response["result"]



if __name__ == "__main__":
    saige = SAIGE()
    while True:
        query = input("query: ")
        if query == 'q':
            break
        answer = saige.query(query=query)
        print(f"answer: {answer}")
