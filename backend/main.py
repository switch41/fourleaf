"""
FastAPI backend for the voter verification system.
"""

from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File
from fastapi.security import APIKeyHeader, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import numpy as np
import cv2
from datetime import datetime
import io
from loguru import logger

from ai.utils.verification import FingerprintVerifier
from ai.config import (
    API_CONFIG,
    SECURITY_CONFIG,
    VERIFICATION_CONFIG,
    LOGGING_CONFIG
)

# Initialize FastAPI app
app = FastAPI(
    title="Voter Verification System API",
    description="API for AI & Blockchain-based voter verification",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
api_key_header = APIKeyHeader(name="X-API-Key")
security = HTTPBearer()

# Initialize verifier
verifier = FingerprintVerifier(
    similarity_threshold=VERIFICATION_CONFIG["similarity_threshold"],
    use_minutiae=VERIFICATION_CONFIG["use_minutiae"]
)

# Request/Response models
class VerificationRequest(BaseModel):
    voter_id: str
    polling_station: str
    timestamp: datetime

class VerificationResponse(BaseModel):
    success: bool
    confidence: float
    metadata: Dict[str, Any]
    transaction_hash: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Helper functions
async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key."""
    # In production, implement proper API key verification
    if api_key != "your-secret-api-key":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

async def process_image(file: UploadFile) -> np.ndarray:
    """Process uploaded image file."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image format"
            )
            
        return image
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Error processing image"
        )

# API endpoints
@app.post("/verify",
          response_model=VerificationResponse,
          responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
          dependencies=[Depends(verify_api_key)])
async def verify_fingerprint(
    fingerprint: UploadFile = File(...),
    voter_id: str = None,
    polling_station: str = None
):
    """
    Verify a voter's fingerprint.
    
    Args:
        fingerprint: Fingerprint image file
        voter_id: Voter's unique identifier
        polling_station: Polling station identifier
        
    Returns:
        Verification result with confidence score and metadata
    """
    try:
        # Process uploaded image
        image = await process_image(fingerprint)
        
        # TODO: Fetch stored features from blockchain
        # This is a placeholder - implement actual blockchain integration
        stored_features = np.random.rand(512)  # Placeholder
        stored_minutiae = (np.random.rand(10, 2), np.random.randint(0, 2, 10))  # Placeholder
        
        # Verify fingerprint
        result, confidence, metadata = verifier.verify_fingerprint(
            image,
            stored_features,
            stored_minutiae
        )
        
        # TODO: Record verification on blockchain
        # This is a placeholder - implement actual blockchain integration
        transaction_hash = "0x123..."  # Placeholder
        
        return VerificationResponse(
            success=result,
            confidence=confidence,
            metadata=metadata,
            transaction_hash=transaction_hash
        )
        
    except Exception as e:
        logger.error(f"Error in verification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/config")
async def get_config():
    """Get system configuration (non-sensitive)."""
    return {
        "version": "1.0.0",
        "features": {
            "minutiae_verification": VERIFICATION_CONFIG["use_minutiae"],
            "max_attempts": VERIFICATION_CONFIG["max_verification_attempts"],
            "timeout": VERIFICATION_CONFIG["verification_timeout"]
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        workers=API_CONFIG["workers"],
        timeout_keep_alive=API_CONFIG["timeout"],
        reload=True
    ) 