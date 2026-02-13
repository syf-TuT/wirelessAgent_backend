"""Enumeration types for the application."""
from enum import Enum


class SliceType(str, Enum):
    """Network slice types."""

    EMBB = "eMBB"
    URLLC = "URLLC"
    MMTC = "mMTC"


class AllocationStatus(str, Enum):
    """Resource allocation status."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class IntentCategory(str, Enum):
    """Intent classification categories."""

    HIGH_BANDWIDTH = "high_bandwidth"
    LOW_LATENCY = "low_latency"
    MASSIVE_CONNECTIVITY = "massive_connectivity"
    UNKNOWN = "unknown"


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
