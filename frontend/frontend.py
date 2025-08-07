import streamlit as st
import requests
from langchain.schema import HumanMessage, AIMessage
import base64
import mimetypes

st.set_page_config(page_title="QA RAG BOT", page_icon="")
st.title("QA RAG BOT")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = []

if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = "uploaded_files_0"

if "files_processed" not in st.session_state:
    st.session_state.files_processed = False

use_multimodal = st.toggle("📷 Use Multimodal", key="use_multimodal")

image_types = ["image/jpeg", "image/png", "image/jpg"]

mime_type = ""

multimodal_image_data = ""

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
uploaded_files = st.file_uploader("＋", 
                                 type=["pdf", "txt", "csv", "docx", "jpg", "jpeg", "png", "db", "sqlite", "xlsx", "json", "md"], 
                                 label_visibility="collapsed", 
                                 key=st.session_state.file_uploader_key,
                                 accept_multiple_files=True)
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_files:
    uploaded_names = [f.name for f in uploaded_files]

    if uploaded_names != st.session_state.uploaded_file_name:
        with st.spinner("Uploading..."):
            try:
                files = [("file", (file.name, file.getvalue())) for file in uploaded_files]
                response = requests.post("http://fastapi:8000/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"{result['message']}")
                    for fname in result["filename"]:
                        st.toast(f"Uploaded: {fname}", icon="📁")
                    st.session_state.uploaded_file_name = uploaded_names
                    if use_multimodal:
                        for file in uploaded_files:
                            mime_type, _ = mimetypes.guess_type(file.name)
                            if mime_type in image_types:
                                st.session_state.base64_image_url = base64.b64encode(file.getvalue()).decode("utf-8")
                                break
                else:
                    st.error(f"Upload failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
for i, message in enumerate(st.session_state.chat_history):
    if isinstance(message, HumanMessage):
        with st.chat_message("User"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("Rag Bot"):
            st.markdown(f"💬 Final Response: \n{message.content}")
            if f"context_{i}" in st.session_state:
                with st.expander("📄 Contexts"):
                    st.markdown(st.session_state[f"context_{i}"])
            if f"source_info_{i}" in st.session_state:
                with st.expander("📚 Source Info"):
                    source_info = st.session_state[f"source_info_{i}"]
                    if isinstance(source_info, list):
                        for src in source_info:
                            st.markdown(f"- {src}")
                    else:
                        st.markdown(str(source_info))

if use_multimodal and "base64_image_url" in st.session_state:
    base64_image_url = st.session_state.base64_image_url
else:
    base64_image_url = st.text_input("🔗 Optional base64 encoded image or image URL:", placeholder="Paste your base64 encoded image or image url here...")

user_query = st.chat_input("You")
if user_query:
    st.session_state.chat_history.append(HumanMessage(user_query))

    with st.chat_message("User"):
        st.markdown(user_query)

    with st.chat_message("Rag Bot"):
        try:
            payload = {
                "query": user_query,
                "base64_image_url": base64_image_url if base64_image_url else None
            }
            response = requests.post("http://fastapi:8000/query", json=payload)
            st.session_state.pop("base64_image_url", None)
            if response.status_code == 200:
                result = response.json()
                if "Response" in result:
                    st.markdown(f"💬 Final Response: \n{result['Response']}")
                if "Context" in result:
                    with st.expander("📄 Contexts"):
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
                message_index = len(st.session_state.chat_history) - 1
                if "Context" in result:
                    st.session_state[f"context_{message_index}"] = result["Context"]
                if "Source Info" in result:
                    st.session_state[f"source_info_{message_index}"] = result["Source Info"]
                
                st.session_state.uploaded_file_name = []
                st.session_state.file_uploader_key = f"uploaded_files_{len(st.session_state.chat_history)}"
                st.rerun()
                
            else:
                st.error(f"Query failed: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")