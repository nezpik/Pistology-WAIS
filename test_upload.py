import streamlit as st
import os
import tempfile

st.title("File Upload Test")

# Use a temporary directory for uploads
temp_dir = tempfile.gettempdir()

# Simple file uploader with explicit key
uploaded_file = st.file_uploader(
    "Choose a file", 
    type=['txt'],
    key="file_uploader",
    accept_multiple_files=False,
    help="Upload a text file to test the functionality"
)

if uploaded_file is not None:
    # Display file details
    st.write("Filename:", uploaded_file.name)
    st.write("File size:", uploaded_file.size, "bytes")
    
    # Save the file to temp directory
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', dir=temp_dir) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name
            
        st.success(f"File saved successfully")
        
        # Display file contents
        with open(file_path, 'r') as f:
            content = f.read()
        st.text("File contents:")
        st.code(content)
        
        # Clean up
        os.unlink(file_path)
    except Exception as e:
        st.error(f"Error handling file: {str(e)}")
        st.error("Full error details:", exc_info=True)
