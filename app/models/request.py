"""
Request and Response Pydantic models.

This module defines models for API request/response schemas including
allocation requests/responses, intent understanding, and network state.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field, field_validator

from app.models.enums import AllocationStatus, IntentType, SliceType
from app.models.user import UserLocation, UserRequest

if TYPE_CHECKING:
    from app.models.network import GlobalNetworkState


class AllocationRequest(BaseModel):
    """
    Request model for resource allocation.

    This is the main input for creating a new resource allocation.
    It includes all necessary information about the user, their location,
    request, and channel quality.

    Attributes:
        user_id: Unique identifier for the user
        location: User's 3D geographical location
        request: Natural language service request
        cqi: Channel Quality Indicator (1-15)
        ground_truth: Optional ground truth for testing

    Example:
        >>> request = AllocationRequest(
        ...     user_id="user_001",
        ...     location=UserLocation(x=75.64, y=182.46, z=1.50),
        ...     request=UserRequest(text="I need to stream 4K video"),
        ...     cqi=12,
        ...     ground_truth="eMBB"
        ... )
        >>> print(request.user_id)
        user_001
    """

    user_id: str = Field(
        ...,
        description="Unique user identifier",
        min_length=1,
        max_length=100,
        examples=["user_001", "session_abc123"],
    )
    location: UserLocation = Field(
        ...,
        description="User's 3D geographical location",
    )
    request: UserRequest = Field(
        ...,
        description="Natural language service request",
    )
    cqi: int = Field(
        ...,
        description="Channel Quality Indicator (1-15, higher is better)",
        ge=1,
        le=15,
        examples=[1, 7, 12, 15],
    )
    ground_truth: Optional[str] = Field(
        default=None,
        description="Ground truth slice type for testing/evaluation",
        examples=["eMBB", "URLLC", "mMTC"],
    )

    @field_validator("ground_truth")
    @classmethod
    def validate_ground_truth(cls, v: Optional[str]) -> Optional[str]:
        """Validate ground truth value if provided."""
        if v is not None:
            valid_values = {"eMBB", "URLLC", "mMTC", "EMBB", "URLLC", "MMTC"}
            if v.upper() not in {g.upper() for g in valid_values}:
                raise ValueError(f"ground_truth must be one of eMBB, URLLC, mMTC, got {v}")
        return v


class AllocationResponse(BaseModel):
    """
    Response model for resource allocation.

    This is the output of a resource allocation operation, containing
    all details about the allocation including bandwidth, rate, latency,
    and status information.

    Attributes:
        user_id: Unique identifier for the user
        slice_type: Allocated network slice type
        bandwidth: Allocated bandwidth in MHz
        rate: Calculated data rate in Mbps
        latency: Expected latency in milliseconds
        snr: Signal-to-Noise Ratio in dB
        status: Allocation status
        message: Status message or error details

    Example:
        >>> response = AllocationResponse(
        ...     user_id="user_001",
        ...     slice_type=SliceType.EMBB,
        ...     bandwidth=20.0,
        ...     rate=100.5,
        ...     latency=10.0,
        ...     snr=15.0,
        ...     status=AllocationStatus.SUCCESS,
        ...     message="Allocation successful"
        ... )
        >>> print(response.status)
        AllocationStatus.success
    """

    user_id: str = Field(
        ...,
        description="Unique user identifier",
        examples=["user_001", "session_abc123"],
    )
    slice_type: SliceType = Field(
        ...,
        description="Allocated network slice type",
        examples=[SliceType.EMBB, SliceType.URLLC],
    )
    bandwidth: float = Field(
        ...,
        description="Allocated bandwidth in MHz",
        gt=0,
        examples=[20.0, 10.0, 5.0],
    )
    rate: float = Field(
        ...,
        description="Calculated data rate in Mbps",
        gt=0,
        examples=[100.5, 50.0, 10.0],
    )
    latency: float = Field(
        ...,
        description="Expected latency in milliseconds",
        gt=0,
        examples=[10.0, 1.0, 100.0],
    )
    snr: float = Field(
        ...,
        description="Signal-to-Noise Ratio in dB",
        gt=0,
        examples=[15.0, 20.0, 10.0],
    )
    status: AllocationStatus = Field(
        default=AllocationStatus.PENDING,
        description="Current allocation status",
        examples=[AllocationStatus.SUCCESS, AllocationStatus.FAILED],
    )
    message: Optional[str] = Field(
        default=None,
        description="Status message or error details",
        examples=["Allocation successful", "Insufficient resources"],
    )

    def mark_success(self, message: Optional[str] = None) -> None:
        """Mark allocation as successful."""
        self.status = AllocationStatus.SUCCESS
        if message:
            self.message = message

    def mark_failed(self, message: str) -> None:
        """Mark allocation as failed."""
        self.status = AllocationStatus.FAILED
        self.message = message

    def mark_adjusted(self, message: str) -> None:
        """Mark allocation as adjusted."""
        self.status = AllocationStatus.ADJUSTED
        self.message = message

    @property
    def is_successful(self) -> bool:
        """Check if allocation was successful."""
        return self.status == AllocationStatus.SUCCESS

    @property
    def is_failed(self) -> bool:
        """Check if allocation failed."""
        return self.status == AllocationStatus.FAILED


class IntentUnderstandRequest(BaseModel):
    """
    Request model for intent understanding/classification.

    Used to classify a user's natural language request into an intent type
    without performing actual resource allocation.

    Attributes:
        request: Natural language service request text
        use_knowledge_base: Whether to use knowledge base for classification

    Example:
        >>> request = IntentUnderstandRequest(
        ...     request="I need to stream 4K video for a conference",
        ...     use_knowledge_base=True
        ... )
        >>> print(request.request)
        I need to stream 4K video for a conference
    """

    request: str = Field(
        ...,
        description="Natural language service request text",
        min_length=1,
        max_length=5000,
        examples=[
            "I need to stream 4K video for a conference",
            "Control a surgical robot remotely with minimal delay",
            "Monitor 1000 IoT sensors in my factory",
        ],
    )
    use_knowledge_base: bool = Field(
        default=True,
        description="Whether to use knowledge base for classification",
        examples=[True, False],
    )

    @field_validator("request")
    @classmethod
    def validate_request_not_empty(cls, v: str) -> str:
        """Ensure request text is not empty after stripping."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Request text cannot be empty or whitespace only")
        return stripped


class IntentUnderstandResponse(BaseModel):
    """
    Response model for intent understanding/classification.

    Contains the classified intent type, confidence score, and
    mapped network slice type.

    Attributes:
        intent_type: Classified intent type (broadband, low_latency, iot)
        confidence: Confidence score (0.0 to 1.0)
        slice_type: Mapped network slice type (eMBB, URLLC, mMTC)
        explanation: Explanation of the classification
        used_knowledge_base: Whether knowledge base was used

    Example:
        >>> response = IntentUnderstandResponse(
        ...     intent_type=IntentType.BROADBAND,
        ...     confidence=0.95,
        ...     slice_type=SliceType.EMBB,
        ...     explanation="Video streaming requires high bandwidth",
        ...     used_knowledge_base=True
        ... )
        >>> print(response.confidence)
        0.95
    """

    intent_type: IntentType = Field(
        ...,
        description="Classified intent type",
        examples=[IntentType.BROADBAND, IntentType.LOW_LATENCY, IntentType.IOT],
    )
    confidence: float = Field(
        ...,
        description="Classification confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
        examples=[0.95, 0.8, 0.6],
    )
    slice_type: SliceType = Field(
        ...,
        description="Mapped network slice type",
        examples=[SliceType.EMBB, SliceType.URLLC, SliceType.MMTC],
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Explanation of the classification decision",
        examples=[
            "Video streaming requires high bandwidth",
            "Remote control requires low latency",
            "IoT sensors require massive connectivity",
        ],
    )
    used_knowledge_base: bool = Field(
        default=False,
        description="Whether knowledge base was used for classification",
        examples=[True, False],
    )

    @field_validator("explanation")
    @classmethod
    def validate_explanation(cls, v: Optional[str]) -> Optional[str]:
        """Ensure explanation is not empty if provided."""
        if v is not None:
            stripped = v.strip()
            if not stripped:
                return None
            return stripped
        return v


class NetworkStateResponse(BaseModel):
    """
    Response model for network state queries.

    Provides a complete snapshot of the current network state
    including all slices, their capacities, and utilization.

    Attributes:
        embb_slice: eMBB slice state
        urllc_slice: URLLC slice state
        mmtc_slice: mMTC slice state
        total_capacity: Total capacity across all slices (MHz)
        total_used_capacity: Total used capacity (MHz)
        total_available_capacity: Total available capacity (MHz)
        total_users: Total number of allocated users
        utilization_percentage: Overall network utilization (%)
        last_updated: Timestamp of last update

    Example:
        >>> from app.models.enums import SliceType
        >>> response = NetworkStateResponse(
        ...     embb_slice=NetworkSlice(
        ...         slice_type=SliceType.EMBB,
        ...         capacity=SliceCapacity(total_capacity=90, resource_usage=30)
        ...     ),
        ...     urllc_slice=NetworkSlice(
        ...         slice_type=SliceType.URLLC,
        ...         capacity=SliceCapacity(total_capacity=30, resource_usage=10)
        ...     ),
        ...     mmtc_slice=NetworkSlice(
        ...         slice_type=SliceType.MMTC,
        ...         capacity=SliceCapacity(total_capacity=10, resource_usage=5)
        ...     )
        ... )
        >>> print(response.total_capacity)
        130.0
    """

    embb_slice: "NetworkSlice" = Field(
        ...,
        description="eMBB (Enhanced Mobile Broadband) slice state",
    )
    urllc_slice: "NetworkSlice" = Field(
        ...,
        description="URLLC (Ultra-Reliable Low-Latency) slice state",
    )
    mmtc_slice: "NetworkSlice" = Field(
        ...,
        description="mMTC (Massive Machine-Type Communications) slice state",
    )
    total_capacity: float = Field(
        ...,
        description="Total capacity across all slices (MHz)",
        ge=0,
        examples=[130.0, 90.0],
    )
    total_used_capacity: float = Field(
        ...,
        description="Total used capacity (MHz)",
        ge=0,
        examples=[30.0, 45.5],
    )
    total_available_capacity: float = Field(
        ...,
        description="Total available capacity (MHz)",
        ge=0,
        examples=[100.0, 44.5],
    )
    total_users: int = Field(
        ...,
        description="Total number of allocated users",
        ge=0,
        examples=[0, 5, 100],
    )
    utilization_percentage: float = Field(
        ...,
        description="Overall network utilization percentage",
        ge=0,
        le=100,
        examples=[0.0, 25.5, 75.0],
    )
    last_updated: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of last update",
        examples=["2024-01-15T10:30:00Z"],
    )

    @classmethod
    def from_global_state(
        cls, state: "GlobalNetworkState"
    ) -> "NetworkStateResponse":
        """
        Create a response from a GlobalNetworkState instance.

        Args:
            state: The global network state

        Returns:
            NetworkStateResponse populated from the state
        """
        return cls(
            embb_slice=state.embb_slice,
            urllc_slice=state.urllc_slice,
            mmtc_slice=state.mmtc_slice,
            total_capacity=state.total_capacity,
            total_used_capacity=state.total_used_capacity,
            total_available_capacity=state.total_available_capacity,
            total_users=state.total_users,
            utilization_percentage=state.utilization_percentage,
            last_updated=state.last_updated,
        )


class ErrorResponse(BaseModel):
    """
    Standard error response model.

    Provides a consistent format for API error responses.

    Attributes:
        error: Error type or code
        message: Human-readable error message
        details: Additional error details
        request_id: Optional request ID for tracing

    Example:
        >>> error = ErrorResponse(
        ...     error="VALIDATION_ERROR",
        ...     message="Invalid CQI value",
        ...     details={"field": "cqi", "value": 20}
        ... )
        >>> print(error.message)
        Invalid CQI value
    """

    error: str = Field(
        ...,
        description="Error type or code",
        examples=["VALIDATION_ERROR", "NOT_FOUND", "INSUFFICIENT_RESOURCES"],
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Invalid CQI value", "User not found"],
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details",
        examples=[{"field": "cqi", "value": 20}],
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for tracing",
        examples=["req_abc123"],
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "CQI must be between 1 and 15",
                "details": {"field": "cqi", "provided": 20, "allowed": "1-15"},
                "request_id": "req_abc123",
            }
        }