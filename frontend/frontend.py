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
    st.session_state.uploaded_file_name = None

use_multimodal = st.toggle("📷 Use Multimodal", key="use_multimodal")

image_types = ["image/jpeg", "image/png", "image/png"]

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
uploaded_file = st.file_uploader("＋", type=["pdf", "txt", "csv", "docx", "jpg", "jpeg", "png", "db", "sqlite", "xlsx", "json", "md"], label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file and st.session_state.uploaded_file_name != uploaded_file.name:
    mime_type, _ = mimetypes.guess_type(uploaded_file.name)
    with st.spinner("Uploading..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        try:
            response = requests.post("http://fastapi:8000/upload", files=files)
            if response.status_code == 200:
                result = response.json()
                st.success(f"{result['message']}")
                st.toast(f"Uploaded: {result['filename']}", icon="📁")
                st.session_state.uploaded_file_name = uploaded_file.name
                if use_multimodal and mime_type in image_types:
                    st.session_state.base64_image_url = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
            else:
                st.error(f"Upload failed: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
if use_multimodal and "base64_image_url" in st.session_state:
    base64_image_url = st.session_state.base64_image_url
else:
    base64_image_url = st.text_input("🔗 Optional base64 image link:", placeholder="Paste your base64 image URL here...")
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
                    st.markdown(f"💬 Final Response\n{result['Response']}")
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
            else:
                st.error(f"Query failed: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")