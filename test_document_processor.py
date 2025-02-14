from agents.document_processor import DocumentProcessor
import os
import logging

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("Initializing document processor...")
    
    # Initialize the processor with settings optimized for laptops
    processor = DocumentProcessor(
        batch_size=3,  # Process 3 documents at a time
        max_workers=2  # Use 2 worker threads to be conservative
    )
    
    # Get all PDF and text files in the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = []
    for root, _, files in os.walk(current_dir):
        for file in files:
            if file.lower().endswith(('.pdf', '.txt', '.docx')):
                full_path = os.path.join(root, file)
                test_files.append(full_path)
                logger.info(f"Found document: {full_path}")
    
    if not test_files:
        logger.warning("No test documents found. Please add some PDF, TXT, or DOCX files to test.")
        return
        
    logger.info(f"Found {len(test_files)} documents to process")
    logger.info("Starting document processing...")
    
    try:
        # Process the documents
        results = processor.process_documents(test_files)
        
        # Print results
        logger.info(f"\nProcessed {len(results)} documents successfully")
        
        # Get system stats
        stats = processor.get_system_stats()
        logger.info("\nSystem Statistics:")
        logger.info(f"Peak memory usage: {stats['peak_memory_mb']:.2f} MB")
        logger.info(f"Current memory usage: {stats['current_memory_mb']:.2f} MB")
        logger.info(f"Batch size used: {stats['batch_size']}")
        logger.info(f"Worker threads used: {stats['max_workers']}")
        
        # Print document details
        for i, doc in enumerate(results, 1):
            logger.info(f"\nDocument {i}:")
            logger.info(f"Source: {doc.metadata.get('source', 'Unknown')}")
            logger.info(f"File type: {doc.metadata.get('file_type', 'Unknown')}")
            logger.info(f"Size: {doc.metadata.get('size', 0) / 1024:.2f} KB")
            # Print first 100 characters of content
            content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            logger.info(f"Content preview: {content_preview}")
            
    except Exception as e:
        logger.error(f"Error during document processing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
