"""
Network State API Endpoints.

This module provides RESTful endpoints for managing and monitoring network state,
including checking current resource usage, viewing slice capacity, and resetting
network state for testing.

Endpoints:
    GET /api/v1/network/state - Get current network state
    POST /api/v1/network/reset - Reset network state
    GET /api/v1/network/slices - Get all slice details
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.state_manager import StateManager

# Create router
router = APIRouter(prefix="/network", tags=["network"])

# Service instances
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get or create the StateManager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


class SliceInfo(BaseModel):
    """Information about a network slice."""
    
    slice_type: str
    total_capacity: float
    resource_usage: float
    available_capacity: float
    usage_percentage: float
    active_users: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "slice_type": "eMBB",
                "total_capacity": 90.0,
                "resource_usage": 45.0,
                "available_capacity": 45.0,
                "usage_percentage": 50.0,
                "active_users": 3,
            }
        }


class NetworkStateResponse(BaseModel):
    """Response model for network state."""
    
    embb: SliceInfo
    urllc: SliceInfo
    mmtc: SliceInfo
    total_capacity: float
    total_usage: float
    total_available: float
    system_usage_percentage: float
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "embb": {
                    "slice_type": "eMBB",
                    "total_capacity": 90.0,
                    "resource_usage": 45.0,
                    "available_capacity": 45.0,
                    "usage_percentage": 50.0,
                    "active_users": 3,
                },
                "urllc": {
                    "slice_type": "URLLC",
                    "total_capacity": 30.0,
                    "resource_usage": 15.0,
                    "available_capacity": 15.0,
                    "usage_percentage": 50.0,
                    "active_users": 2,
                },
                "mmtc": {
                    "slice_type": "mMTC",
                    "total_capacity": 10.0,
                    "resource_usage": 5.0,
                    "available_capacity": 5.0,
                    "usage_percentage": 50.0,
                    "active_users": 1,
                },
                "total_capacity": 130.0,
                "total_usage": 65.0,
                "total_available": 65.0,
                "system_usage_percentage": 50.0,
                "timestamp": "2025-02-15T10:30:45.123456",
            }
        }


class ResetResponse(BaseModel):
    """Response model for reset operation."""
    
    status: str
    message: str
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Network state reset successfully",
                "timestamp": "2025-02-15T10:30:45.123456",
            }
        }


@router.get("/state", response_model=NetworkStateResponse)
async def get_network_state() -> NetworkStateResponse:
    """
    Get the current network state and resource utilization.
    
    Returns detailed information about all network slices including capacity,
    current usage, available resources, and number of active users per slice.
    
    Returns:
        NetworkStateResponse: Current state of all network slices
        
    Example:
        >>> GET /api/v1/network/state
        {
            "embb": {
                "slice_type": "eMBB",
                "total_capacity": 90,
                "resource_usage": 45,
                ...
            },
            ...
        }
    """
    try:
        state_mgr = get_state_manager()
        state = state_mgr.get_global_state()
        
        # Calculate metrics for each slice
        embb_state = state.get("embb_slice", {})
        urllc_state = state.get("urllc_slice", {})
        mmtc_state = state.get("mmtc_slice", {})
        
        def create_slice_info(slice_data, slice_name):
            total = slice_data.get("total_capacity", 0)
            usage = slice_data.get("resource_usage", 0)
            available = max(0, total - usage)
            usage_pct = (usage / total * 100) if total > 0 else 0
            
            return SliceInfo(
                slice_type=slice_name,
                total_capacity=total,
                resource_usage=usage,
                available_capacity=available,
                usage_percentage=round(usage_pct, 2),
                active_users=len(slice_data.get("users", [])),
            )
        
        embb_info = create_slice_info(embb_state, "eMBB")
        urllc_info = create_slice_info(urllc_state, "URLLC")
        mmtc_info = create_slice_info(mmtc_state, "mMTC")
        
        total_cap = embb_info.total_capacity + urllc_info.total_capacity + mmtc_info.total_capacity
        total_usage = embb_info.resource_usage + urllc_info.resource_usage + mmtc_info.resource_usage
        total_avail = total_cap - total_usage
        system_usage_pct = (total_usage / total_cap * 100) if total_cap > 0 else 0
        
        from datetime import datetime
        
        return NetworkStateResponse(
            embb=embb_info,
            urllc=urllc_info,
            mmtc=mmtc_info,
            total_capacity=total_cap,
            total_usage=total_usage,
            total_available=total_avail,
            system_usage_percentage=round(system_usage_pct, 2),
            timestamp=datetime.utcnow().isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get network state: {str(e)}",
        )


@router.post("/reset", response_model=ResetResponse)
async def reset_network_state() -> ResetResponse:
    """
    Reset network state to initial conditions.
    
    Clears all resource allocations and resets all slices to zero usage.
    Useful for testing and demo purposes.
    
    Returns:
        ResetResponse: Status of reset operation
        
    Example:
        >>> POST /api/v1/network/reset
        {
            "status": "success",
            "message": "Network state reset successfully",
            "timestamp": "2025-02-15T10:30:45.123456"
        }
    """
    try:
        state_mgr = get_state_manager()
        state_mgr.reset_state()
        
        from datetime import datetime
        
        return ResetResponse(
            status="success",
            message="Network state reset successfully",
            timestamp=datetime.utcnow().isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset network state: {str(e)}",
        )


@router.get("/slices", response_model=Dict[str, SliceInfo])
async def get_slice_details() -> Dict[str, SliceInfo]:
    """
    Get detailed information about all network slices.
    
    Returns:
        Dictionary with slice type as key and SliceInfo as value
        
    Example:
        >>> GET /api/v1/network/slices
        {
            "eMBB": {...},
            "URLLC": {...},
            "mMTC": {...}
        }
    """
    try:
        state_mgr = get_state_manager()
        state = state_mgr.get_global_state()
        
        embb_state = state.get("embb_slice", {})
        urllc_state = state.get("urllc_slice", {})
        mmtc_state = state.get("mmtc_slice", {})
        
        def create_slice_info(slice_data, slice_name):
            total = slice_data.get("total_capacity", 0)
            usage = slice_data.get("resource_usage", 0)
            available = max(0, total - usage)
            usage_pct = (usage / total * 100) if total > 0 else 0
            
            return SliceInfo(
                slice_type=slice_name,
                total_capacity=total,
                resource_usage=usage,
                available_capacity=available,
                usage_percentage=round(usage_pct, 2),
                active_users=len(slice_data.get("users", [])),
            )
        
        return {
            "eMBB": create_slice_info(embb_state, "eMBB"),
            "URLLC": create_slice_info(urllc_state, "URLLC"),
            "mMTC": create_slice_info(mmtc_state, "mMTC"),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get slice details: {str(e)}",
        )
