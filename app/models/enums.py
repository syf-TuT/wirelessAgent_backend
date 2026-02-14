"""Enumeration types for the application."""
from enum import Enum


class SliceType(str, Enum):
    """Network slice types."""

    EMBB = "eMBB"
    URLLC = "URLLC"
    MMTC = "mMTC"


class AllocationStatus(str, Enum):
    """Resource allocation status."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    ADJUSTED = "adjusted"


class IntentCategory(str, Enum):
    """Intent classification categories."""

    HIGH_BANDWIDTH = "high_bandwidth"
    LOW_LATENCY = "low_latency"
    MASSIVE_CONNECTIVITY = "massive_connectivity"
    UNKNOWN = "unknown"


class IntentType(str, Enum):
    """User intent classification types.

    Maps user requests to the appropriate network slice type:
    - BROADBAND: High bandwidth needs (maps to eMBB)
    - LOW_LATENCY: Critical real-time needs (maps to URLLC)
    - IOT: Massive device connectivity (maps to mMTC)
    - UNKNOWN: Could not determine intent
    """

    BROADBAND = "broadband"  # High bandwidth (eMBB)
    LOW_LATENCY = "low_latency"  # Low latency (URLLC)
    IOT = "iot"  # IoT devices (mMTC)
    UNKNOWN = "unknown"  # Could not determine

    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value


def get_slice_type_from_intent(intent: IntentType) -> SliceType:
    """Map intent type to the appropriate network slice type.

    Args:
        intent: The classified user intent

    Returns:
        The corresponding network slice type
    """
    mapping = {
        IntentType.BROADBAND: SliceType.EMBB,
        IntentType.LOW_LATENCY: SliceType.URLLC,
        IntentType.IOT: SliceType.MMTC,
        IntentType.UNKNOWN: SliceType.EMBB,  # Default to eMBB
    }
    return mapping.get(intent, SliceType.EMBB)


class TaskStatus(str, Enum):
    """Background task status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
