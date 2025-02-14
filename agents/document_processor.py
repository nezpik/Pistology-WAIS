from typing import List, Dict, Any, Optional
import os
import logging
from dataclasses import dataclass
from langchain_community.document_loaders import TextLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import psutil

@dataclass
class ProcessingResult:
    success: bool
    document_text: str = ""
    document_metadata: Dict[str, Any] = None
    error: str = ""

class DocumentProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "total_size_mb": 0
        }
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "processing_stats": {
                    "total_processed": self.stats["total_processed"],
                    "successful": self.stats["successful"],
                    "failed": self.stats["failed"],
                    "total_size_mb": self.stats["total_size_mb"]
                },
                "system_info": {
                    "current_memory_mb": memory_info.rss / 1024 / 1024,
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads()
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting system stats: {str(e)}")
            return {
                "processing_stats": self.stats,
                "system_info": {}
            }
            
    def _check_file_validity(self, file_path: str) -> Optional[str]:
        """Check if file exists and is accessible"""
        if not os.path.exists(file_path):
            return f"File does not exist: {file_path}"
        if not os.path.isfile(file_path):
            return f"Path is not a file: {file_path}"
        if os.path.getsize(file_path) == 0:
            return f"File is empty: {file_path}"
        return None

    def _process_document(self, file_path: str) -> ProcessingResult:
        """Process a single document using LangChain document loaders"""
        try:
            # Validate file
            if error := self._check_file_validity(file_path):
                self.stats["total_processed"] += 1
                self.stats["failed"] += 1
                return ProcessingResult(success=False, error=error, document_metadata={"file_path": file_path})
                
            # Get file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            self.stats["total_size_mb"] += file_size_mb
            
            # Choose appropriate loader based on file type
            if file_path.lower().endswith('.txt'):
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                loader = UnstructuredFileLoader(file_path)
            
            self.logger.info(f"Loading document: {file_path}")
            docs = loader.load()
            self.logger.info(f"Document loaded successfully: {file_path}")
            
            if not docs:
                self.stats["total_processed"] += 1
                self.stats["failed"] += 1
                return ProcessingResult(
                    success=False,
                    error="No content could be extracted from document",
                    document_metadata={"file_path": file_path, "file_size_mb": file_size_mb}
                )
            
            # Split documents into chunks for better processing
            chunks = self.text_splitter.split_documents(docs)
            
            # Combine all chunks into a single text
            combined_text = "\n\n".join([chunk.page_content for chunk in chunks])
            
            # Create metadata
            metadata = {
                "file_path": file_path,
                "file_size_mb": file_size_mb,
                "num_chunks": len(chunks)
            }
            
            # Add any additional metadata from the first document
            if docs and hasattr(docs[0], 'metadata'):
                metadata.update(docs[0].metadata)
            
            self.stats["total_processed"] += 1
            self.stats["successful"] += 1
            
            return ProcessingResult(
                success=True,
                document_text=combined_text,
                document_metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {str(e)}")
            self.stats["total_processed"] += 1
            self.stats["failed"] += 1
            return ProcessingResult(
                success=False,
                error=str(e),
                document_metadata={"file_path": file_path}
            )

    def process_documents(self, file_paths: List[str]) -> List[ProcessingResult]:
        """Process multiple documents"""
        results = []
        for file_path in file_paths:
            try:
                result = self._process_document(file_path)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing document {file_path}: {str(e)}")
                self.stats["total_processed"] += 1
                self.stats["failed"] += 1
                results.append(ProcessingResult(
                    success=False,
                    error=str(e),
                    document_metadata={"file_path": file_path}
                ))
        return results
