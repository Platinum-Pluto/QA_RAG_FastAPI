"""import streamlit as st

if "chat_history" not in st.session_state:
	st.session_state.chat_history = []

st.set_page_config(page_title = "QA RAG BOT", page_icon = "")
st.title("QA RAG BOT")


user_query = st.chat_input(" You")
if user_query is not None and user_query != "":
	st.session_state.chat_history.append(HumanMessage(user_query)
	with st.chat_message("You"):
		st.markdown(user_query)
	with st.chat_message("Rag Bot"):
		ai_response = st.write_stream(query_rag(user_query, st.session_state.chat_history))
	st.session_state.chat_history.append(AIMessage(ai_response))"""

import streamlit as st
import requests
from langchain.schema import HumanMessage, AIMessage

st.set_page_config(page_title="QA RAG BOT", page_icon="")
st.title("QA RAG BOT")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

upload_css = """
<style>
.upload-container {
    position: absolute;
    top: 1.5rem;
    right: 2rem;
    z-index: 1000;
}
.upload-label {
    background-color: #f0f2f6;
    border-radius: 50%;
    padding: 10px 14px;
    font-size: 20px;
    font-weight: bold;
    color: #333;
    cursor: pointer;
    border: 1px solid #ccc;
}
.upload-label:hover {
    background-color: #e1e4e8;
}
</style>
"""
st.markdown(upload_css, unsafe_allow_html=True)

st.markdown('<div class="upload-container">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("＋", type=["pdf", "txt", "csv", "docx"], label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file and st.session_state.uploaded_file_name != uploaded_file.name:
    with st.spinner("Uploading..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        try:
            response = requests.post("http://localhost:8000/upload", files=files)
            if response.status_code == 200:
                result = response.json()
                st.success(f"{result['message']}")
                st.toast(f"Uploaded: {result['filename']}", icon="📁")
                st.session_state.uploaded_file_name = uploaded_file.name
            else:
                st.error(f"Upload failed: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

user_query = st.chat_input("You")
if user_query:
    st.session_state.chat_history.append(HumanMessage(user_query))

    with st.chat_message("User"):
        st.markdown(user_query)

    with st.chat_message("Rag Bot"):
        try:
            response = requests.post("http://localhost:8000/query", json={"query": user_query})

            if response.status_code == 200:
                result = response.json()

                if "Response" in result:
                    st.markdown(f"💬 Response\n{result['Response']}")
                if "Context" in result:
                    with st.expander("📄 Context"):
                        st.markdown(result["Context"])
                if "Source Info" in result:
                    with st.expander("📚 Source Info"):
                        if isinstance(result["Source Info"], list):
                            for src in result["Source Info"]:
                                st.markdown(f"- {src}")
                        else:
                            st.markdown(str(result["Source Info"]))
                full_bot_message = result.get("Response", "")
                st.session_state.chat_history.append(AIMessage(full_bot_message))
            else:
                st.error(f"Query failed: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")
