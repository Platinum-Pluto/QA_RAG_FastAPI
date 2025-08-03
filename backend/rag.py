from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate
from data_digest import load_file
import os
from dotenv import load_dotenv
import base64
import httpx

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("API_KEY")
llm = init_chat_model(os.getenv("MODEL"), model_provider=os.getenv("PROVIDER"))
llm1 = init_chat_model(os.getenv("MODEL"), model_provider=os.getenv("PROVIDER"))

#I added two of them so that multimodal model and regular text gen model are separate and configurable


class PlatinumPipeline:
    class State(TypedDict):
        question: str
        context: List[Document]
        answer: str

    def __init__(self):
        self.UPLOAD_DIR = "uploads"
        self.llm = llm
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        #self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.vector_store = Chroma(
            collection_name="rag_collection",
            embedding_function=self.embeddings,
        )


        self.prompt_template = """Use the following pieces of context to answer the question.
If you don't know the answer based on the context that has been provided then, just say that you don't know, don't try to make up an answer.
You have to be concise with your answers so that its reasonable and understandable to the user.

Context: {context}

Question: {question}

Helpful Answer:
"""

        self.rag_prompt = PromptTemplate.from_template(self.prompt_template)
        self.rag_docs = None
        self.load_and_process_documents()


    def list_files(self):
        files = []
        for filename in os.listdir(self.UPLOAD_DIR):
            if os.path.isfile(os.path.join(self.UPLOAD_DIR, filename)):
                files.append(filename)
        return files


    def load_and_process_documents(self):
        docs = []
        files = self.list_files()
        for file in files:
            doc = load_file(os.path.join(self.UPLOAD_DIR, file))
            docs.extend(doc)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        all_splits = text_splitter.split_documents(docs)
        self.vector_store.add_documents(documents=all_splits)


    def retrieve(self, state: State):
        retrieved_docs = self.vector_store.similarity_search(state["question"])
        self.vector_store.delete_collection()
        self.rag_docs = None
        self.rag_docs = retrieved_docs
        return {"context": retrieved_docs}


    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.rag_prompt.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}


    def gen_ans(self, question):
        graph_builder = StateGraph(self.State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        response = graph.invoke({"question": question})

        return response["answer"], self.rag_docs
    


def query_image_base64(base64_image: str, query: str) -> str:
    image_data = base64.b64encode(httpx.get(base64_image).content).decode("utf-8")
 
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": query},
            {
                "type": "image",
                "source_type": "base64",
                "data": image_data,
                "mime_type": "image/jpeg",
            },
        ],
    }

    response = llm1.invoke([message])
    return response.text()


