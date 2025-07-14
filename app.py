import streamlit as st
import tempfile
import os
from main import main as process_pdf

st.title("Book PDF Chapter Splitter & Summarizer")

uploaded_file = st.file_uploader("Upload a PDF book", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    st.write("Processing your PDF. This may take a while for large files...")
    process_pdf(tmp_path)
    out_dir = os.path.splitext(tmp_path)[0] + "_chapters"
    if os.path.exists(out_dir):
        st.success(f"Chapters processed! Download below:")
        for fname in os.listdir(out_dir):
            with open(os.path.join(out_dir, fname), "rb") as f:
                st.download_button(f"Download {fname}", f, file_name=fname)
    else:
        st.error("Failed to process PDF.")
