from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
from typing import Optional
import logging
from pf1_comprehensive_extractor import (
    extract_technical_fields_from_text,
    extract_commercial_fields_from_text,
    extract_basic_fields_from_text,
    extract_text_pdfco
)
from pf1_quote_extractor_full import extract_quotes_from_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Structura.AI Backend",
    description="FastAPI backend for Structura.AI quote extraction service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class PDFExtractionRequest(BaseModel):
    file: Optional[str] = None
    text: Optional[str] = None

class QuoteRequest(BaseModel):
    text: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Structura.AI Backend is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "Structura.AI Backend",
        "version": "1.0.0"
    }

@app.post("/extract-pdf")
async def extract_pdf_data(
    file: UploadFile = File(...)
):
    """
    Extract comprehensive data from PDF file
    
    Args:
        file: Uploaded PDF file
    
    Returns:
        JSON response with extracted technical, commercial, and basic data
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text from PDF
        logger.info(f"Processing PDF: {file.filename}")
        extracted_text = extract_text_pdfco(temp_file_path)
        
        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )
        
        # Extract all three types of data
        technical_data = extract_technical_fields_from_text(extracted_text, file.filename)
        commercial_data = extract_commercial_fields_from_text(extracted_text, file.filename)
        basic_data = extract_basic_fields_from_text(extracted_text, file.filename)
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "text_length": len(extracted_text),
            "technical_fields": len(technical_data),
            "commercial_fields": len(commercial_data),
            "basic_fields": len(basic_data),
            "data": {
                "technical": technical_data,
                "commercial": commercial_data,
                "basic": basic_data
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/extract-quotes")
async def extract_quotes(
    request: QuoteRequest
):
    """
    Extract quotes from text (legacy endpoint)
    
    Args:
        text: Direct text input
    
    Returns:
        JSON response with extracted quotes
    """
    try:
        # Get text from request
        input_text = request.text
        
        if not input_text or not input_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Text content cannot be empty"
            )
        
        # Extract quotes using the existing logic
        logger.info(f"Processing text of length: {len(input_text)}")
        extracted_quotes = extract_quotes_from_text(input_text)
        
        return JSONResponse({
            "success": True,
            "quotes": extracted_quotes,
            "total_quotes": len(extracted_quotes),
            "text_length": len(input_text)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/v1/info")
async def get_api_info():
    """Get information about the Structura.AI extraction service"""
    return {
        "service": "Structura.AI Comprehensive Extractor",
        "version": "1.0.0",
        "description": "Extract technical, commercial, and basic data from PDFs",
        "endpoints": {
            "extract_pdf": "/extract-pdf",
            "extract_quotes": "/extract-quotes",
            "health": "/health"
        },
        "supported_formats": ["pdf"],
        "extraction_types": {
            "technical": "Engineering specifications and technical details",
            "commercial": "Pricing, terms, and commercial information",
            "basic": "Basic machine details and applications"
        }
    }

@app.post("/extract-quotes-simple")
async def extract_quotes_simple(text: str = Form(...)):
    """Simple endpoint for quote extraction with form data"""
    try:
        if not text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Text content cannot be empty"
            )
        
        # Extract quotes using the existing logic
        logger.info(f"Processing text of length: {len(text)}")
        extracted_quotes = extract_quotes_from_text(text)
        
        return JSONResponse({
            "success": True,
            "quotes": extracted_quotes,
            "total_quotes": len(extracted_quotes),
            "text_length": len(text)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/debug")
async def debug_endpoint(request: QuoteRequest):
    """Debug endpoint to see what's being received"""
    return {
        "received": True,
        "request": request.dict() if request else None,
        "text": request.text if request else None
    }

if __name__ == "__main__":
    # Get port from environment variable (for Railway deployment)
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to False for production
        log_level="info"
    ) 