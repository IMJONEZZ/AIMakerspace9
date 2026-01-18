import fitz  # PyMuPDF
import asyncio
from typing import List


class PDFIngestionPipeline:
    def __init__(self, vector_db, text_splitter):
        """
        Initialize the PDF ingestion pipeline.
        
        Args:
            vector_db: A VectorDatabase instance for storing embeddings
            text_splitter: A text splitter (e.g., CharacterTextSplitter) for chunking text
        """
        self.vector_db = vector_db
        self.text_splitter = text_splitter
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: The complete text extracted from all pages of the PDF
        """
        doc = fitz.open(pdf_path)
        text = ""
        
        for page in doc:
            text += page.get_text()
        
        doc.close()
        return text
    
    def split_text(self, documents: str | List[str]) -> List[str]:
        """
        Split text or list of texts into chunks using the text splitter.
        
        Args:
            documents: Either a single string or list of strings to split
            
        Returns:
            List[str]: Split documents/chunks
        """
        # Ensure we have a list of strings
        if isinstance(documents, str):
            documents = [documents]
        
        split_documents = self.text_splitter.split_texts(documents)
        return split_documents
    
    def add_to_vector_db(self, split_documents: List[str]) -> None:
        """
        Add split documents to the vector database.
        
        Args:
            split_documents: List of text chunks to add to the vector database
        """
        self.vector_db = asyncio.run(self.vector_db.abuild_from_list(split_documents))
