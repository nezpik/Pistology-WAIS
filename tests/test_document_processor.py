import unittest
import os
from agents.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()
        
    def test_process_documents(self):
        # Create a test text file
        test_file = "test_doc.txt"
        with open(test_file, "w") as f:
            f.write("Test document content")
            
        try:
            # Process the test document
            docs = self.processor.process_documents([test_file])
            
            # Verify document was processed
            self.assertTrue(len(docs) > 0)
            
            # Check content extraction
            text = self.processor.extract_text(docs[0])
            self.assertIn("Test document content", text)
            
            # Check metadata
            metadata = self.processor.get_metadata(docs[0])
            self.assertIsInstance(metadata, dict)
            
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
                
if __name__ == '__main__':
    unittest.main()
