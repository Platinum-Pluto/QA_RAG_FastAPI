from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate
from data_digest import load_file
import main


llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


vector_store = Chroma(
    collection_name="rag_collection",
    embedding_function=embeddings,
)

docs = []

for file in main.files:
    doc = load_file(file)
    docs.extend(doc)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
    )

all_splits = text_splitter.split_documents(docs)

vectors = vector_store.add_documents(documents=all_splits)


prompt_template = """Use the following pieces of context to answer the question.
If you don't know the answer based on the context that has been provided then, just say that you don't know, don't try to make up an answer.
You have to be concise with your answers so that its reasonable and understandable to the user.

{context}

Question: {question}

Helpful Answer:
"""

rag_prompt = PromptTemplate.from_template(prompt_template)

rag_docs = None


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


def retrieve(state: State):
    retrieved_docs = vectors.similarity_search(state["question"])
    global rag_docs
    rag_docs = retrieved_docs
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = rag_prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


def gen_ans(question):
    global rag_docs
    context = rag_docs
    rag_docs.clear()
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    response = graph.invoke({"question": "Query"})

    return response["answer"], context