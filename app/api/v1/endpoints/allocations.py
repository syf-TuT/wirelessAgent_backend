"""
Allocations API Endpoints.

This module provides RESTful endpoints for network resource allocation operations.
It handles creating allocations, retrieving allocation results, and managing
the lifecycle of resource allocation requests.

Endpoints:
    POST /api/v1/allocations - Create new resource allocation
    GET /api/v1/allocations/{id} - Get allocation by ID
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.models.request import AllocationRequest, AllocationResponse
from app.services.network_slicing import NetworkSlicingService
from app.services.state_manager import StateManager

# Create router
router = APIRouter(prefix="/allocations", tags=["allocations"])

# Service instances (would normally be dependency-injected)
_state_manager: Optional[StateManager] = None
_service: Optional[NetworkSlicingService] = None


def get_service() -> NetworkSlicingService:
    """Get or create the NetworkSlicingService instance."""
    global _service
    if _service is None:
        global _state_manager
        _state_manager = _state_manager or StateManager()
        _service = NetworkSlicingService(state_manager=_state_manager)
    return _service


# Store allocation results in memory (for demo purposes)
# In production, this would be a database
_allocations_db: Dict[str, AllocationResponse] = {}
_allocation_counter: int = 0


@router.post("", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
async def create_allocation(request: AllocationRequest) -> AllocationResponse:
    """
    Create a new resource allocation.
    
    This endpoint processes a user's service request, understands their intent,
    determines the appropriate network slice (eMBB, URLLC, or mMTC), and
    allocates network resources accordingly.
    
    Args:
        request: Allocation request containing user info, location, and service request
        
    Returns:
        AllocationResponse: Allocation result with bandwidth, rate, latency info
        
    Raises:
        HTTPException: If allocation fails or validation fails
        
    Example:
        >>> request_body = {
        ...     "user_id": "user_001",
        ...     "location": {"x": 75.64, "y": 182.46, "z": 1.50},
        ...     "request": {"text": "I need to stream 4K video"},
        ...     "cqi": 12,
        ...     "ground_truth": "eMBB"
        ... }
        >>> response = POST /api/v1/allocations
    """
    global _allocation_counter, _allocations_db
    
    try:
        service = get_service()
        
        # Convert UserRequest to string for service call
        request_text = (
            request.request.text
            if hasattr(request.request, "text")
            else str(request.request)
        )
        
        # Call the core allocation service
        result = service.allocate_resources(
            user_id=request.user_id,
            request=request_text,
            location=(request.location.x, request.location.y, request.location.z),
            cqi=request.cqi,
            ground_truth=request.ground_truth,
        )
        
        # Generate allocation ID
        allocation_id = f"alloc_{_allocation_counter}"
        _allocation_counter += 1
        
        # Create response model from result
        response = AllocationResponse(
            user_id=result.get("user_id", request.user_id),
            allocation_id=allocation_id,
            slice_type=result.get("slice_type", "unknown"),
            bandwidth=result.get("bandwidth", 0),
            rate=result.get("rate", 0),
            latency=result.get("latency", 0),
            snr=result.get("snr", 0),
            status=result.get("status", "success"),
            message=result.get("message", "Allocation successful"),
            timestamp=result.get("timestamp"),
            ground_truth=request.ground_truth,
        )
        
        # Store in memory DB
        _allocations_db[allocation_id] = response
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Allocation failed: {str(e)}",
        )


@router.get("/{allocation_id}", response_model=AllocationResponse)
async def get_allocation(allocation_id: str) -> AllocationResponse:
    """
    Get allocation details by ID.
    
    Retrieves a previously created allocation result by its ID.
    
    Args:
        allocation_id: The allocation ID from the creation response
        
    Returns:
        AllocationResponse: The full allocation details
        
    Raises:
        HTTPException: If allocation not found
        
    Example:
        >>> GET /api/v1/allocations/alloc_0
    """
    if allocation_id not in _allocations_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allocation {allocation_id} not found",
        )
    
    return _allocations_db[allocation_id]


@router.get("", response_model=List[AllocationResponse])
async def list_allocations(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    slice_type: Optional[str] = Query(None, description="Filter by slice type"),
    status: Optional[str] = Query(None, description="Filter by status"),
) -> List[AllocationResponse]:
    """
    List all allocations with optional filtering.
    
    Args:
        user_id: Optional filter by user ID
        slice_type: Optional filter by slice type (eMBB, URLLC, mMTC)
        status: Optional filter by status
        
    Returns:
        List of allocations matching filters
        
    Example:
        >>> GET /api/v1/allocations?user_id=user_001&slice_type=eMBB
    """
    results = list(_allocations_db.values())
    
    # Apply filters
    if user_id:
        results = [a for a in results if a.user_id == user_id]
    if slice_type:
        results = [a for a in results if a.slice_type.upper() == slice_type.upper()]
    if status:
        results = [a for a in results if a.status == status]
    
    return results
