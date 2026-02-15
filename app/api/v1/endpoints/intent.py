"""
Intent Understanding API Endpoints.

This module provides RESTful endpoints for intent classification and understanding
without performing full resource allocation. It allows clients to test and verify
intent classification independently.

Endpoints:
    POST /api/v1/intent/understand - Classify intent from a service request
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.enums import IntentType
from app.services.intent_understanding import IntentUnderstandingService

# Create router
router = APIRouter(prefix="/intent", tags=["intent"])

# Service instances
_intent_service: Optional[IntentUnderstandingService] = None


def get_intent_service() -> IntentUnderstandingService:
    """Get or create the IntentUnderstandingService instance."""
    global _intent_service
    if _intent_service is None:
        _intent_service = IntentUnderstandingService(use_knowledge_base=False)
    return _intent_service


class IntentRequest(BaseModel):
    """Request model for intent understanding."""
    
    user_request: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language service request",
        examples=["I need to stream 4K video", "I want to control a drone"],
    )
    ground_truth: Optional[str] = Field(
        default=None,
        description="Optional ground truth for evaluation",
        examples=["eMBB", "URLLC", "mMTC"],
    )


class IntentConfidence(BaseModel):
    """Confidence scores for each intent type."""
    
    embb: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score for eMBB (0-1)",
    )
    urllc: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score for URLLC (0-1)",
    )
    mmtc: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score for mMTC (0-1)",
    )


class IntentResponse(BaseModel):
    """Response model for intent understanding."""
    
    user_request: str
    identified_intent: str = Field(
        description="Classified intent type (eMBB, URLLC, or mMTC)",
        examples=["eMBB", "URLLC", "mMTC"],
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score for the identified intent (0-1)",
    )
    confidence_scores: Optional[IntentConfidence] = Field(
        default=None,
        description="Detailed confidence scores for all intent types",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Explanation of the classification decision",
    )
    ground_truth: Optional[str] = Field(
        default=None,
        description="Ground truth if provided in request",
    )
    is_correct: Optional[bool] = Field(
        default=None,
        description="Whether classification matches ground truth (if provided)",
    )
    timestamp: str = Field(
        description="Timestamp of the classification",
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_request": "I need to stream 4K video",
                "identified_intent": "eMBB",
                "confidence": 0.95,
                "confidence_scores": {
                    "embb": 0.95,
                    "urllc": 0.03,
                    "mmtc": 0.02,
                },
                "reasoning": "Video streaming requires high bandwidth and throughput, characteristic of eMBB services",
                "ground_truth": "eMBB",
                "is_correct": True,
                "timestamp": "2025-02-15T10:30:45.123456",
            }
        }


@router.post("/understand", response_model=IntentResponse)
async def understand_intent(request: IntentRequest) -> IntentResponse:
    """
    Classify and understand user intent from a service request.
    
    This endpoint analyzes a natural language service request and classifies
    it into one of three network slice types: eMBB (Enhanced Mobile Broadband),
    URLLC (Ultra-Reliable Low-Latency), or mMTC (Massive Machine-Type Communication).
    
    It returns confidence scores and optionally compares against ground truth
    if provided.
    
    Args:
        request: Intent request containing user request and optional ground truth
        
    Returns:
        IntentResponse: Classification result with confidence scores and reasoning
        
    Raises:
        HTTPException: If intent classification fails
        
    Example:
        >>> POST /api/v1/intent/understand
        >>> Request body:
        {
            "user_request": "I need to stream 4K video",
            "ground_truth": "eMBB"
        }
        >>> Response:
        {
            "user_request": "I need to stream 4K video",
            "identified_intent": "eMBB",
            "confidence": 0.95,
            ...
        }
    """
    try:
        intent_service = get_intent_service()
        
        # Classify the intent
        result = intent_service.understand_intent(request.user_request)
        
        from datetime import datetime
        
        # Extract classification result
        identified_intent = result.get("intent", "unknown")
        confidence = result.get("confidence", 0.0)
        reasoning = result.get("reasoning", "")
        
        # Determine if classification is correct (if ground truth provided)
        is_correct = None
        if request.ground_truth:
            # Normalize for comparison
            gt_upper = request.ground_truth.upper().replace("EMBB", "EMBB").replace("MMTC", "MMTC")
            identified_upper = identified_intent.upper().replace("EMBB", "EMBB").replace("MMTC", "MMTC")
            is_correct = gt_upper == identified_upper
        
        # Try to get confidence scores if available
        confidence_scores = None
        if "confidence_scores" in result:
            try:
                scores = result["confidence_scores"]
                confidence_scores = IntentConfidence(
                    embb=scores.get("eMBB", scores.get("EMBB", 0.0)),
                    urllc=scores.get("URLLC", 0.0),
                    mmtc=scores.get("mMTC", scores.get("MMTC", 0.0)),
                )
            except Exception:
                pass
        
        return IntentResponse(
            user_request=request.user_request,
            identified_intent=identified_intent,
            confidence=confidence,
            confidence_scores=confidence_scores,
            reasoning=reasoning,
            ground_truth=request.ground_truth,
            is_correct=is_correct,
            timestamp=datetime.utcnow().isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent classification failed: {str(e)}",
        )


@router.get("/examples", response_model=dict)
async def get_intent_examples() -> dict:
    """
    Get examples of requests for each intent type.
    
    Returns common examples of user requests that are classified as each
    network slice type (eMBB, URLLC, mMTC).
    
    Returns:
        Dictionary with intent types and example requests
        
    Example:
        >>> GET /api/v1/intent/examples
    """
    return {
        "eMBB": {
            "description": "Enhanced Mobile Broadband - High data rate, best effort",
            "examples": [
                "I need to stream 4K video",
                "I want to download large files",
                "I need high-speed AR/VR experience",
                "I want to upload multiple large videos",
            ],
        },
        "URLLC": {
            "description": "Ultra-Reliable Low-Latency - Low latency, high reliability",
            "examples": [
                "I need to control a surgical robot remotely",
                "I want to drive an autonomous vehicle",
                "I need to monitor critical infrastructure in real-time",
                "I need ultra-low latency for gaming",
            ],
        },
        "mMTC": {
            "description": "Massive Machine-Type Communication - Many devices, low bandwidth",
            "examples": [
                "I need to connect hundreds of IoT sensors",
                "I want to read smart meters from thousands of homes",
                "I need to track asset locations across a large area",
                "I want to collect environmental sensing data",
            ],
        },
    }
