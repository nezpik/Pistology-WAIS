from langchain_docling import DoclingLoader
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    FILE_PATH = ["https://arxiv.org/pdf/2408.09869"]  # Docling Technical Report
    
    try:
        logging.info("Initializing DoclingLoader...")
        loader = DoclingLoader(file_path=FILE_PATH)
        logging.info("Loading documents...")
        docs = loader.load()
        
        logging.info(f"Number of documents loaded: {len(docs)}")
        if docs:
            logging.info("First document content preview:")
            logging.info(docs[0].page_content[:500])
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logging.error(f"Response content: {e.response.content}")

if __name__ == "__main__":
    main()
