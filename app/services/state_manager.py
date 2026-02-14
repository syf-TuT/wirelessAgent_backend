"""
StateManager - Manages global network state and slice capacity tracking
"""

from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from app.models.enums import SliceType


class StateManager:
    """
    Manages persistent network state including slice capacity, resource usage, and user allocation.
    
    In production, this should interface with a database. Currently uses in-memory state.
    """
    
    # Default network slice capacities (in MHz)
    DEFAULT_CAPACITIES = {
        SliceType.EMBB: 90,      # Enhanced Mobile Broadband: 90 MHz
        SliceType.URLLC: 30,     # Ultra-Reliable Low-Latency: 30 MHz
        SliceType.MMTC: 10,      # Massive Machine-Type Communications: 10 MHz
    }
    
    def __init__(self, capacities: Optional[Dict[SliceType, float]] = None):
        """
        Initialize StateManager with optional custom capacities.
        
        Args:
            capacities: Optional dictionary of {SliceType: capacity_in_mhz}
        """
        self.capacities = capacities or self.DEFAULT_CAPACITIES.copy()
        self._reset_state()
    
    def _reset_state(self):
        """Initialize or reset the global network state"""
        self.state: Dict[str, Any] = {
            SliceType.EMBB: {
                "users": [],                              # List of allocated users
                "total_capacity": self.capacities[SliceType.EMBB],
                "resource_usage": 0.0,                    # Current bandwidth usage in MHz
                "utilization_rate": "0%",
                "total_transmission_rate": 0.0,          # Sum of all user rates
            },
            SliceType.URLLC: {
                "users": [],
                "total_capacity": self.capacities[SliceType.URLLC],
                "resource_usage": 0.0,
                "utilization_rate": "0%",
                "total_transmission_rate": 0.0,
            },
            SliceType.MMTC: {
                "users": [],
                "total_capacity": self.capacities[SliceType.MMTC],
                "resource_usage": 0.0,
                "utilization_rate": "0%",
                "total_transmission_rate": 0.0,
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_users": 0,
        }
        self.initial_state = self._deep_copy_state(self.state)
        self.previous_state = None
    
    def _deep_copy_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deep copy of the network state"""
        import copy
        return copy.deepcopy(state)
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current network state.
        
        Returns:
            Dictionary containing current state of all slices
        """
        return self._deep_copy_state(self.state)
    
    def update_state(self, new_state: Dict[str, Any]) -> bool:
        """
        Update the global network state.
        
        Args:
            new_state: New state dictionary to apply
            
        Returns:
            True if update successful
        """
        self.previous_state = self._deep_copy_state(self.state)
        self.state = self._deep_copy_state(new_state)
        return True
    
    def reset_to_initial(self) -> bool:
        """
        Reset network state to initial values for fresh testing.
        
        Returns:
            True if reset successful
        """
        self.state = self._deep_copy_state(self.initial_state)
        self.state["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.previous_state = None
        return True
    
    def allocate_user(self, slice_type: SliceType, user_info: Dict[str, Any]) -> bool:
        """
        Allocate a user to a specific slice with their resource requirements.
        
        Args:
            slice_type: Target slice (eMBB, URLLC, mMTC)
            user_info: Dictionary containing user allocation details
                      (user_id, bandwidth, rate, latency, etc.)
                      
        Returns:
            True if allocation successful, False if slice full
            
        Raises:
            ValueError: If slice type invalid or user_info missing required fields
        """
        if slice_type not in self.state:
            raise ValueError(f"Invalid slice type: {slice_type}")
        
        if "user_id" not in user_info or "bandwidth" not in user_info:
            raise ValueError("user_info must contain 'user_id' and 'bandwidth'")
        
        slice_data = self.state[slice_type]
        required_bandwidth = user_info.get("bandwidth", 0)
        available = slice_data["total_capacity"] - slice_data["resource_usage"]
        
        # Check if slice has enough capacity
        if required_bandwidth > available:
            return False
        
        # Add user to slice
        slice_data["users"].append(user_info)
        slice_data["resource_usage"] += required_bandwidth
        slice_data["total_transmission_rate"] += user_info.get("rate", 0)
        
        # Update utilization rate
        self._update_utilization_rates()
        
        # Update total users
        self.state["total_users"] += 1
        
        # Update timestamp
        self.state["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return True
    
    def deallocate_user(self, slice_type: SliceType, user_id: str) -> bool:
        """
        Remove a user from a slice.
        
        Args:
            slice_type: Source slice (eMBB, URLLC, mMTC)
            user_id: User identifier to deallocate
            
        Returns:
            True if deallocation successful, False if user not found
        """
        if slice_type not in self.state:
            return False
        
        slice_data = self.state[slice_type]
        
        # Find and remove user
        user_to_remove = None
        for user in slice_data["users"]:
            if user.get("user_id") == user_id:
                user_to_remove = user
                break
        
        if not user_to_remove:
            return False
        
        # Remove user and update resources
        slice_data["users"].remove(user_to_remove)
        slice_data["resource_usage"] -= user_to_remove.get("bandwidth", 0)
        slice_data["total_transmission_rate"] -= user_to_remove.get("rate", 0)
        
        # Ensure non-negative values
        slice_data["resource_usage"] = max(0, slice_data["resource_usage"])
        slice_data["total_transmission_rate"] = max(0, slice_data["total_transmission_rate"])
        
        # Update utilization rate
        self._update_utilization_rates()
        
        # Update total users
        self.state["total_users"] = max(0, self.state["total_users"] - 1)
        
        # Update timestamp
        self.state["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return True
    
    def get_slice_status(self, slice_type: SliceType) -> Dict[str, Any]:
        """
        Get detailed status of a specific slice.
        
        Args:
            slice_type: Slice to query (eMBB, URLLC, mMTC)
            
        Returns:
            Dictionary with slice status (available bandwidth, utilization, users, etc.)
        """
        if slice_type not in self.state:
            raise ValueError(f"Invalid slice type: {slice_type}")
        
        slice_data = self.state[slice_type]
        available_bw = slice_data["total_capacity"] - slice_data["resource_usage"]
        
        return {
            "slice_type": slice_type,
            "total_capacity": slice_data["total_capacity"],
            "resource_usage": slice_data["resource_usage"],
            "available_bandwidth": available_bw,
            "utilization_rate": slice_data["utilization_rate"],
            "total_transmission_rate": slice_data["total_transmission_rate"],
            "user_count": len(slice_data["users"]),
            "users": slice_data["users"],
        }
    
    def get_all_slices_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all slices.
        
        Returns:
            Dictionary with status of all three slices
        """
        return {
            SliceType.EMBB: self.get_slice_status(SliceType.EMBB),
            SliceType.URLLC: self.get_slice_status(SliceType.URLLC),
            SliceType.MMTC: self.get_slice_status(SliceType.MMTC),
        }
    
    def get_available_bandwidth(self, slice_type: SliceType) -> float:
        """
        Get available bandwidth in a slice.
        
        Args:
            slice_type: Slice to query (eMBB, URLLC, mMTC)
            
        Returns:
            Available bandwidth in MHz
        """
        if slice_type not in self.state:
            raise ValueError(f"Invalid slice type: {slice_type}")
        
        slice_data = self.state[slice_type]
        return slice_data["total_capacity"] - slice_data["resource_usage"]
    
    def can_allocate(self, slice_type: SliceType, required_bandwidth: float) -> bool:
        """
        Check if a slice has enough capacity for allocation.
        
        Args:
            slice_type: Slice to check (eMBB, URLLC, mMTC)
            required_bandwidth: Required bandwidth in MHz
            
        Returns:
            True if enough capacity available
        """
        return self.get_available_bandwidth(slice_type) >= required_bandwidth
    
    def get_utilization_rates(self) -> Dict[SliceType, float]:
        """
        Get current utilization rates for all slices.
        
        Returns:
            Dictionary mapping slice type to utilization rate (0.0-1.0)
        """
        rates = {}
        for slice_type in [SliceType.EMBB, SliceType.URLLC, SliceType.MMTC]:
            slice_data = self.state[slice_type]
            rate = slice_data["resource_usage"] / slice_data["total_capacity"]
            rates[slice_type] = rate
        return rates
    
    def _update_utilization_rates(self):
        """Update utilization rate percentages for all slices"""
        for slice_type in [SliceType.EMBB, SliceType.URLLC, SliceType.MMTC]:
            slice_data = self.state[slice_type]
            rate = (slice_data["resource_usage"] / slice_data["total_capacity"]) * 100
            slice_data["utilization_rate"] = f"{rate:.2f}%"
    
    def is_slice_full(self, slice_type: SliceType) -> bool:
        """
        Check if a slice has reached its capacity limit.
        
        Args:
            slice_type: Slice to check (eMBB, URLLC, mMTC)
            
        Returns:
            True if slice is at full capacity
        """
        return self.get_available_bandwidth(slice_type) <= 0.0
    
    def get_least_utilized_slice(self) -> SliceType:
        """
        Get the slice with the lowest utilization.
        
        Returns:
            SliceType enum of least utilized slice
        """
        rates = self.get_utilization_rates()
        return min(rates.keys(), key=lambda k: rates[k])
    
    def get_most_utilized_slice(self) -> SliceType:
        """
        Get the slice with the highest utilization.
        
        Returns:
            SliceType enum of most utilized slice
        """
        rates = self.get_utilization_rates()
        return max(rates.keys(), key=lambda k: rates[k])
