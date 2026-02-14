"""Data models for the application."""
from app.models.enums import (
    AllocationStatus,
    IntentCategory,
    IntentType,
    LogLevel,
    SliceType,
    TaskStatus,
    get_slice_type_from_intent,
)
from app.models.network import (
    NetworkSlice,
    NetworkState,
    SliceCapacity,
    SliceUser,
)
from app.models.user import (
    AllocationResult,
    ResourceAllocation,
    User,
    UserLocation,
    UserRequest,
)

# Import new F003 models from request module
try:
    from app.models.request import (
        AllocationRequest,
        AllocationResponse,
        ErrorResponse,
        IntentUnderstandRequest,
        IntentUnderstandResponse,
        NetworkStateResponse,
    )
    _request_models_available = True
except ImportError:
    _request_models_available = False

__all__ = [
    # Enums
    "SliceType",
    "AllocationStatus",
    "IntentCategory",
    "IntentType",
    "TaskStatus",
    "LogLevel",
    "get_slice_type_from_intent",
    # Network models
    "NetworkSlice",
    "NetworkState",
    "SliceCapacity",
    "SliceUser",
    # User models
    "User",
    "UserRequest",
    "UserLocation",
    "AllocationResult",
    "ResourceAllocation",
]

# Add request/response models if available
if _request_models_available:
    __all__.extend([
        "AllocationRequest",
        "AllocationResponse",
        "IntentUnderstandRequest",
        "IntentUnderstandResponse",
        "NetworkStateResponse",
        "ErrorResponse",
    ])
