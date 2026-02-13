"""Network slice and resource models."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.enums import SliceType


class SliceCapacity(BaseModel):
    """Slice capacity configuration."""

    total_capacity: float = Field(..., description="Total capacity in MHz", ge=0)
    resource_usage: float = Field(default=0, description="Current resource usage in MHz", ge=0)
    utilization_rate: str = Field(default="0%", description="Utilization rate as percentage")

    @property
    def available_capacity(self) -> float:
        """Calculate available capacity."""
        return max(0, self.total_capacity - self.resource_usage)


class NetworkSlice(BaseModel):
    """Network slice definition."""

    slice_type: SliceType = Field(..., description="Slice type")
    capacity: SliceCapacity = Field(..., description="Slice capacity")
    users: List["SliceUser"] = Field(default_factory=list, description="Assigned users")
    min_bandwidth: float = Field(..., description="Minimum bandwidth per user in MHz")
    max_bandwidth: float = Field(..., description="Maximum bandwidth per user in MHz")
    min_latency: float = Field(..., description="Minimum latency in ms")
    max_latency: float = Field(..., description="Maximum latency in ms")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "slice_type": "eMBB",
                "capacity": {
                    "total_capacity": 90,
                    "resource_usage": 45,
                    "utilization_rate": "50%"
                },
                "min_bandwidth": 6,
                "max_bandwidth": 20,
                "min_latency": 10,
                "max_latency": 100
            }
        }


class SliceUser(BaseModel):
    """User assigned to a network slice."""

    user_id: str = Field(..., description="User identifier")
    slice_type: SliceType = Field(..., description="Assigned slice type")
    cqi: int = Field(..., description="Channel Quality Indicator", ge=1, le=15)
    bandwidth: float = Field(..., description="Allocated bandwidth in MHz", ge=0)
    rate: float = Field(..., description="Allocated data rate in Mbps", ge=0)
    latency: float = Field(..., description="Allocated latency in ms", ge=0)
    request: str = Field(..., description="Original user request")
    timestamp: datetime = Field(default_factory=datetime.now, description="Assignment timestamp")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "1",
                "slice_type": "eMBB",
                "cqi": 12,
                "bandwidth": 15,
                "rate": 129.58,
                "latency": 50,
                "request": "I want to stream 4K video"
            }
        }


class NetworkState(BaseModel):
    """Complete network state."""

    embb_slice: NetworkSlice = Field(..., description="eMBB slice state")
    urllc_slice: NetworkSlice = Field(..., description="URLLC slice state")
    mmtc_slice: NetworkSlice = Field(..., description="mMTC slice state")
    timestamp: datetime = Field(default_factory=datetime.now, description="State timestamp")
    total_users: int = Field(default=0, description="Total number of users", ge=0)

    @property
    def total_resource_usage(self) -> float:
        """Calculate total resource usage across all slices."""
        return (
            self.embb_slice.capacity.resource_usage +
            self.urllc_slice.capacity.resource_usage +
            self.mmtc_slice.capacity.resource_usage
        )

    @property
    def total_capacity(self) -> float:
        """Calculate total capacity across all slices."""
        return (
            self.embb_slice.capacity.total_capacity +
            self.urllc_slice.capacity.total_capacity +
            self.mmtc_slice.capacity.total_capacity
        )

    @property
    def overall_utilization(self) -> float:
        """Calculate overall network utilization."""
        if self.total_capacity == 0:
            return 0.0
        return (self.total_resource_usage / self.total_capacity) * 100

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "embb_slice": {
                    "slice_type": "eMBB",
                    "capacity": {"total_capacity": 90, "resource_usage": 45, "utilization_rate": "50%"},
                    "min_bandwidth": 6,
                    "max_bandwidth": 20,
                    "min_latency": 10,
                    "max_latency": 100
                },
                "urllc_slice": {
                    "slice_type": "URLLC",
                    "capacity": {"total_capacity": 30, "resource_usage": 10, "utilization_rate": "33%"},
                    "min_bandwidth": 1,
                    "max_bandwidth": 5,
                    "min_latency": 1,
                    "max_latency": 10
                },
                "mmtc_slice": {
                    "slice_type": "mMTC",
                    "capacity": {"total_capacity": 10, "resource_usage": 2, "utilization_rate": "20%"},
                    "min_bandwidth": 0.1,
                    "max_bandwidth": 3,
                    "min_latency": 100,
                    "max_latency": 1000
                },
                "total_users": 10
            }
        }


# Update forward references
NetworkSlice.model_rebuild()
