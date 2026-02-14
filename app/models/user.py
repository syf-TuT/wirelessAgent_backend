"""User and allocation models."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import AllocationStatus, SliceType


class UserLocation(BaseModel):
    """User geographic location."""

    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(default=1.5, description="Z coordinate (height) in meters")

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"


class User(BaseModel):
    """Complete user model with location, CQI, and request information."""

    user_id: str = Field(
        ...,
        description="Unique user identifier",
        min_length=1,
        max_length=100,
    )
    location: UserLocation = Field(
        ...,
        description="User's 3D geographical location",
    )
    cqi: int = Field(
        ...,
        description="Channel Quality Indicator (1-15, higher is better)",
        ge=1,
        le=15,
    )
    request: "UserRequest" = Field(
        ...,
        description="User's service request",
    )
    ground_truth: Optional[str] = Field(
        default=None,
        description="Ground truth slice type for testing/evaluation",
    )

    def __str__(self) -> str:
        """Return string representation."""
        return f"User(id={self.user_id}, cqi={self.cqi}, location={self.location})"


class UserRequest(BaseModel):
    """User request for network resources."""

    user_id: str = Field(..., description="Unique user identifier")
    location: UserLocation = Field(..., description="User location")
    request_text: str = Field(
        ...,
        description="User request description",
        min_length=1,
        max_length=1000
    )
    cqi: int = Field(
        ...,
        description="Channel Quality Indicator (1-15)",
        ge=1,
        le=15
    )
    ground_truth: Optional[SliceType] = Field(
        default=None,
        description="Ground truth slice type for evaluation"
    )

    @field_validator("request_text")
    @classmethod
    def validate_request_text(cls, v: str) -> str:
        """Validate request text is not empty after stripping."""
        if not v.strip():
            raise ValueError("Request text cannot be empty")
        return v.strip()


class ResourceAllocation(BaseModel):
    """Resource allocation result."""

    bandwidth: float = Field(..., description="Allocated bandwidth in MHz", ge=0)
    rate: float = Field(..., description="Allocated data rate in Mbps", ge=0)
    latency: float = Field(..., description="Allocated latency in ms", ge=0)


class AllocationResult(BaseModel):
    """Complete allocation result for a user request."""

    user_id: str = Field(..., description="User identifier")
    request_id: str = Field(..., description="Unique request identifier")
    slice_type: SliceType = Field(..., description="Allocated slice type")
    status: AllocationStatus = Field(..., description="Allocation status")
    resources: Optional[ResourceAllocation] = Field(
        default=None,
        description="Allocated resources"
    )
    intent_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Intent analysis results"
    )
    ground_truth: Optional[SliceType] = Field(
        default=None,
        description="Ground truth for evaluation"
    )
    intent_correct: Optional[bool] = Field(
        default=None,
        description="Whether intent was correctly identified"
    )
    adjustments_made: bool = Field(
        default=False,
        description="Whether dynamic adjustments were made"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "user_id": "1",
                "request_id": "req-001",
                "slice_type": "URLLC",
                "status": "success",
                "resources": {
                    "bandwidth": 5.0,
                    "rate": 38.95,
                    "latency": 5.0
                }
            }
        }
