"""
Advanced Document Processor using IBM Docling with fallback to LangChain.

Processes various document formats and adds content to system context
for agent access. Supports PDF, Word, Excel, PowerPoint, images, and more.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from datetime import datetime
import json
import os
import psutil

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logging.warning("Docling not available. Using fallback processors.")

# Fallback imports
from langchain_community.document_loaders import TextLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dataclasses import dataclass
from pydantic import BaseModel, Field


@dataclass
class ProcessingResult:
    """Legacy processing result for backward compatibility"""
    success: bool
    document_text: str = ""
    document_metadata: Dict[str, Any] = None
    error: str = ""


class ProcessedDocument(BaseModel):
    """Structured representation of a processed document"""
    file_path: str
    file_name: str
    file_type: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    success: bool
    error: Optional[str] = None
    processing_time: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class DocumentProcessor:
    """
    Advanced document processor with Docling and fallback support.

    Features:
    - IBM Docling for advanced document parsing
    - LangChain fallback for compatibility
    - Context management for agent access
    - Table and image extraction
    - Search capabilities
    """

    def __init__(self):
        """Initialize document processor"""
        self.logger = logging.getLogger(__name__)

        # Initialize Docling if available
        if DOCLING_AVAILABLE:
            try:
                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True
                pipeline_options.do_table_structure = True

                self.converter = DocumentConverter(
                    allowed_formats=[
                        InputFormat.PDF,
                        InputFormat.DOCX,
                        InputFormat.PPTX,
                        InputFormat.IMAGE,
                        InputFormat.HTML,
                        InputFormat.MD,
                    ]
                )
                self.logger.info("Docling converter initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Docling: {e}. Using fallback.")
                self.converter = None
        else:
            self.converter = None

        # Fallback LangChain tools
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Document storage
        self.processed_documents: List[ProcessedDocument] = []
        self.document_context: Dict[str, str] = {}  # filename -> content mapping

        # Statistics
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "total_size_mb": 0
        }

        self.logger.info(f"Document Processor initialized (Docling: {DOCLING_AVAILABLE})")

    def process_file(self, file_path: str) -> ProcessedDocument:
        """
        Process a single file and extract content.

        Args:
            file_path: Path to the file to process

        Returns:
            ProcessedDocument with extracted content and metadata
        """
        start_time = datetime.now()
        file_path_obj = Path(file_path)

        try:
            if not file_path_obj.exists():
                return ProcessedDocument(
                    file_path=file_path,
                    file_name=file_path_obj.name,
                    file_type="unknown",
                    content="",
                    success=False,
                    error=f"File not found: {file_path}",
                    processing_time=0
                )

            # Try Docling first
            if self.converter and DOCLING_AVAILABLE:
                return self._process_with_docling(file_path_obj, start_time)
            else:
                return self._process_with_fallback(file_path_obj, start_time)

        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()

            self.stats["total_processed"] += 1
            self.stats["failed"] += 1

            return ProcessedDocument(
                file_path=str(file_path_obj.absolute()),
                file_name=file_path_obj.name,
                file_type=file_path_obj.suffix,
                content="",
                success=False,
                error=str(e),
                processing_time=processing_time
            )

    def _process_with_docling(self, file_path: Path, start_time: datetime) -> ProcessedDocument:
        """Process file using Docling"""
        try:
            result = self.converter.convert(str(file_path))

            # Extract content
            content = result.document.export_to_markdown()

            # Extract tables if present
            tables = []
            if hasattr(result.document, 'tables') and result.document.tables:
                for i, table in enumerate(result.document.tables):
                    try:
                        tables.append({
                            "id": i,
                            "markdown": str(table),
                            "row_count": getattr(table, 'row_count', 0)
                        })
                    except Exception as e:
                        self.logger.warning(f"Error extracting table {i}: {e}")

            # Extract metadata
            file_size = file_path.stat().st_size
            metadata = {
                "page_count": getattr(result.document, 'page_count', 0),
                "language": getattr(result.document, 'language', 'unknown'),
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "processor": "docling"
            }

            processing_time = (datetime.now() - start_time).total_seconds()

            doc = ProcessedDocument(
                file_path=str(file_path.absolute()),
                file_name=file_path.name,
                file_type=file_path.suffix,
                content=content,
                metadata=metadata,
                tables=tables,
                success=True,
                processing_time=processing_time
            )

            # Add to context
            self.processed_documents.append(doc)
            self.document_context[file_path.name] = content

            # Update stats
            self.stats["total_processed"] += 1
            self.stats["successful"] += 1
            self.stats["total_size_mb"] += metadata["file_size_mb"]

            self.logger.info(f"Docling processed {file_path.name} in {processing_time:.2f}s")

            return doc

        except Exception as e:
            self.logger.warning(f"Docling failed for {file_path.name}, trying fallback: {e}")
            return self._process_with_fallback(file_path, start_time)

    def _process_with_fallback(self, file_path: Path, start_time: datetime) -> ProcessedDocument:
        """Fallback processing using LangChain and simple text extraction"""
        try:
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)

            # Try text files directly
            if file_path.suffix in ['.txt', '.md', '.csv', '.json']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                # Try UnstructuredFileLoader
                try:
                    if file_path.suffix == '.txt':
                        loader = TextLoader(str(file_path), encoding='utf-8')
                    else:
                        loader = UnstructuredFileLoader(str(file_path))

                    docs = loader.load()
                    chunks = self.text_splitter.split_documents(docs)
                    content = "\n\n".join([chunk.page_content for chunk in chunks])
                except Exception as e:
                    self.logger.warning(f"LangChain loader failed: {e}")
                    content = f"[Binary file: {file_path.name} - Content extraction not available]"

            metadata = {
                "file_size": file_size,
                "file_size_mb": round(file_size_mb, 2),
                "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "processor": "fallback"
            }

            processing_time = (datetime.now() - start_time).total_seconds()

            doc = ProcessedDocument(
                file_path=str(file_path.absolute()),
                file_name=file_path.name,
                file_type=file_path.suffix,
                content=content,
                metadata=metadata,
                success=True,
                processing_time=processing_time
            )

            # Add to context
            self.processed_documents.append(doc)
            self.document_context[file_path.name] = content

            # Update stats
            self.stats["total_processed"] += 1
            self.stats["successful"] += 1
            self.stats["total_size_mb"] += file_size_mb

            self.logger.info(f"Fallback processed {file_path.name} in {processing_time:.2f}s")

            return doc

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()

            self.stats["total_processed"] += 1
            self.stats["failed"] += 1

            return ProcessedDocument(
                file_path=str(file_path.absolute()),
                file_name=file_path.name,
                file_type=file_path.suffix,
                content="",
                success=False,
                error=str(e),
                processing_time=processing_time
            )

    def process_documents(self, file_paths: List[str]) -> List[ProcessingResult]:
        """
        Process multiple files (legacy interface for backward compatibility).

        Args:
            file_paths: List of file paths

        Returns:
            List of ProcessingResult objects
        """
        results = []
        for file_path in file_paths:
            doc = self.process_file(file_path)

            # Convert to legacy format
            result = ProcessingResult(
                success=doc.success,
                document_text=doc.content,
                document_metadata=doc.metadata,
                error=doc.error or ""
            )
            results.append(result)

        return results

    def process_multiple_files(self, file_paths: List[str]) -> List[ProcessedDocument]:
        """
        Process multiple files (new interface).

        Args:
            file_paths: List of file paths

        Returns:
            List of ProcessedDocument objects
        """
        return [self.process_file(fp) for fp in file_paths]

    def get_document_context(self) -> Dict[str, str]:
        """
        Get all processed document content for agent context.

        Returns:
            Dictionary mapping filenames to content
        """
        return self.document_context.copy()

    def get_combined_context(self, max_chars: int = 10000) -> str:
        """
        Get combined context from all documents, truncated to max_chars.

        Args:
            max_chars: Maximum characters to return

        Returns:
            Combined document content as string
        """
        if not self.document_context:
            return ""

        combined = "\n\n--- DOCUMENT CONTEXT ---\n\n".join([
            f"📄 {name}\n{content}"
            for name, content in self.document_context.items()
        ])

        if len(combined) > max_chars:
            combined = combined[:max_chars] + f"\n\n[Truncated... {len(self.document_context)} documents total, {len(combined)} chars]"

        return combined

    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Search processed documents for query.

        Args:
            query: Search query

        Returns:
            List of matching documents with excerpts
        """
        results = []
        query_lower = query.lower()

        for name, content in self.document_context.items():
            if query_lower in content.lower():
                # Find context around match
                idx = content.lower().find(query_lower)
                start = max(0, idx - 100)
                end = min(len(content), idx + 100)
                excerpt = "..." + content[start:end] + "..."

                results.append({
                    "filename": name,
                    "excerpt": excerpt,
                    "relevance": content.lower().count(query_lower)
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)

        return results

    def get_system_stats(self) -> Dict[str, Any]:
        """Get processing and system statistics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                "processing_stats": self.stats,
                "document_stats": {
                    "documents_in_context": len(self.document_context),
                    "total_context_size": sum(len(c) for c in self.document_context.values())
                },
                "system_info": {
                    "current_memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads()
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting system stats: {str(e)}")
            return {
                "processing_stats": self.stats,
                "document_stats": {},
                "system_info": {}
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            "documents_in_context": len(self.document_context),
            "average_processing_time": round(
                sum(doc.processing_time for doc in self.processed_documents) /
                len(self.processed_documents), 2
            ) if self.processed_documents else 0,
            "file_types": list(set(doc.file_type for doc in self.processed_documents))
        }

    def clear_context(self):
        """Clear all processed documents and context"""
        self.processed_documents.clear()
        self.document_context.clear()
        self.logger.info("Document context cleared")

    def export_context(self, output_path: str):
        """
        Export document context to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        export_data = {
            "documents": [doc.dict() for doc in self.processed_documents],
            "statistics": self.get_statistics(),
            "timestamp": datetime.now().isoformat()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Context exported to {output_path}")
