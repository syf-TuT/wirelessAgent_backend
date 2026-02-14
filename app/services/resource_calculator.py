"""
ResourceCalculator - Implements network resource calculation algorithms
"""

import math
import random
from typing import Dict, Any, Tuple
from app.models.enums import SliceType


class ResourceCalculator:
    """
    Implements network resource calculation algorithms including:
    - Shannon's formula for data rate calculation
    - Bandwidth allocation based on CQI and slice type
    - Latency calculations
    - Dynamic bandwidth adjustment
    """
    
    # Bandwidth constraints for each slice type
    SLICE_CONSTRAINTS = {
        SliceType.EMBB: {
            "min_bandwidth": 6.0,
            "default_bandwidth": 12.0,
            "max_bandwidth": 20.0,
            "min_latency": 10,
            "max_latency": 100,
        },
        SliceType.URLLC: {
            "min_bandwidth": 1.0,
            "default_bandwidth": 2.5,
            "max_bandwidth": 5.0,
            "min_latency": 1,
            "max_latency": 10,
        },
        SliceType.MMTC: {
            "min_bandwidth": 0.5,
            "default_bandwidth": 1.5,
            "max_bandwidth": 3.0,
            "min_latency": 100,
            "max_latency": 1000,
        },
    }
    
    # CQI to SNR mapping (CQI value 1-15 to estimated SNR in dB)
    CQI_TO_SNR = {
        1: -6.5,
        2: -4.0,
        3: -1.5,
        4: 1.0,
        5: 3.0,
        6: 5.5,
        7: 8.0,
        8: 10.3,
        9: 12.6,
        10: 14.3,
        11: 15.7,
        12: 17.4,
        13: 19.0,
        14: 20.6,
        15: 22.7,
    }
    
    @staticmethod
    def generate_random_cqi() -> int:
        """
        Generate a random CQI value between 1 and 15.
        
        Returns:
            Random CQI value
        """
        return random.randint(1, 15)
    
    @staticmethod
    def cqi_to_snr(cqi: int) -> float:
        """
        Convert CQI value to estimated SNR in dB.
        
        Args:
            cqi: Channel Quality Indicator (1-15)
            
        Returns:
            Estimated SNR in dB
        """
        # Clamp CQI to valid range
        cqi = max(1, min(15, cqi))
        
        # Use lookup table if available
        if cqi in ResourceCalculator.CQI_TO_SNR:
            return ResourceCalculator.CQI_TO_SNR[cqi]
        
        # Linear interpolation fallback
        return -6.5 + (cqi - 1) * 2.4
    
    @staticmethod
    def calculate_rate_from_cqi(bandwidth: float, cqi: int) -> float:
        """
        Calculate data transmission rate using Shannon's formula.
        
        Formula: Rate = Bandwidth * log2(1 + SNR) = Bandwidth * log10(1 + SNR) * log10(2)
        
        For compatibility with existing system, uses: Rate = Bandwidth * log10(1 + SNR) * 10
        
        Args:
            bandwidth: Allocated bandwidth in MHz
            cqi: Channel Quality Indicator (1-15)
            
        Returns:
            Calculated transmission rate in Mbps
        """
        # Convert CQI to linear SNR
        snr = 10 ** (cqi / 10)
        
        # Calculate rate using Shannon's formula
        # Note: Using log10 scaled by 10 for compatibility with existing system
        rate = bandwidth * math.log10(1 + snr) * 10
        
        # Round to 2 decimal places
        return round(rate, 2)
    
    @staticmethod
    def calculate_latency(bandwidth: float, cqi: int, slice_type: SliceType) -> float:
        """
        Calculate expected latency based on bandwidth, CQI, and slice type.
        
        Args:
            bandwidth: Allocated bandwidth in MHz
            cqi: Channel Quality Indicator (1-15)
            slice_type: Network slice type (eMBB, URLLC, mMTC)
            
        Returns:
            Expected latency in milliseconds
        """
        # Base latency components
        propagation_latency = 5.0  # Standard propagation delay in ms
        
        # Processing latency depends on bandwidth (narrower = more processing)
        processing_latency = max(1.0, 50.0 / bandwidth)
        
        # CQI-based latency (poor signal = higher latency due to retransmissions)
        # CQI 15 = minimal overhead, CQI 1 = maximum overhead
        cqi_factor = (16 - cqi) / 15.0  # 0 to 1
        cqi_latency = cqi_factor * 20.0  # Up to 20ms additional latency
        
        # Slice-specific base latency
        slice_base_latency = {
            SliceType.EMBB: 20.0,
            SliceType.URLLC: 2.0,
            SliceType.MMTC: 100.0,
        }
        
        base = slice_base_latency.get(slice_type, 20.0)
        total_latency = base + propagation_latency + processing_latency + cqi_latency
        
        return round(total_latency, 2)
    
    @staticmethod
    def allocate_bandwidth(
        slice_type: SliceType,
        cqi: int,
        available_bandwidth: float,
        request_priority: str = "default"
    ) -> Dict[str, Any]:
        """
        Determine appropriate bandwidth allocation for a user based on slice type, CQI, and availability.
        
        Args:
            slice_type: Target slice (eMBB, URLLC, mMTC)
            cqi: Channel Quality Indicator (1-15)
            available_bandwidth: Available bandwidth in the slice (MHz)
            request_priority: Priority level ('high', 'default', 'low')
            
        Returns:
            Dictionary with allocation details:
            {
                'allocated_bandwidth': float,
                'min_bandwidth': float,
                'max_bandwidth': float,
                'recommended': bool,  # Whether full recommendation could be met
            }
        """
        constraints = ResourceCalculator.SLICE_CONSTRAINTS.get(slice_type)
        if not constraints:
            raise ValueError(f"Unknown slice type: {slice_type}")
        
        min_bw = constraints["min_bandwidth"]
        default_bw = constraints["default_bandwidth"]
        max_bw = constraints["max_bandwidth"]
        
        # Adjust based on priority
        priority_factors = {"high": 1.2, "default": 1.0, "low": 0.8}
        priority_factor = priority_factors.get(request_priority, 1.0)
        
        # Desired bandwidth considering priority
        desired_bw = default_bw * priority_factor
        
        # CQI adjustment: poor CQI may need higher bandwidth for better rate
        if cqi < 5:
            desired_bw *= 1.1  # Increase for poor signal
        elif cqi > 12:
            desired_bw *= 0.9  # Decrease for excellent signal
        
        # Cap to max constraints
        desired_bw = min(desired_bw, max_bw)
        
        # Check availability
        if available_bandwidth >= desired_bw:
            allocated = desired_bw
            recommended = True
        elif available_bandwidth >= min_bw:
            allocated = available_bandwidth
            recommended = False
        else:
            # Cannot allocate minimum
            return {
                "allocated_bandwidth": 0,
                "min_bandwidth": min_bw,
                "max_bandwidth": max_bw,
                "recommended": False,
            }
        
        return {
            "allocated_bandwidth": round(allocated, 2),
            "min_bandwidth": min_bw,
            "max_bandwidth": max_bw,
            "recommended": recommended,
        }
    
    @staticmethod
    def adjust_bandwidth(
        current_bandwidth: float,
        target_rate: float,
        cqi: int,
        max_bandwidth: float
    ) -> float:
        """
        Adjust bandwidth to achieve a target transmission rate.
        
        Args:
            current_bandwidth: Current allocated bandwidth (MHz)
            target_rate: Desired transmission rate (Mbps)
            cqi: Channel Quality Indicator (1-15)
            max_bandwidth: Maximum allowed bandwidth (MHz)
            
        Returns:
            Adjusted bandwidth in MHz
        """
        # Use Shannon formula to solve for bandwidth
        # target_rate = bandwidth * log10(1 + SNR) * 10
        # bandwidth = target_rate / (log10(1 + SNR) * 10)
        
        snr = 10 ** (cqi / 10)
        shannon_coefficient = math.log10(1 + snr) * 10
        
        if shannon_coefficient <= 0:
            return max_bandwidth
        
        required_bw = target_rate / shannon_coefficient
        
        # Clamp to maximum
        return min(required_bw, max_bandwidth)
    
    @staticmethod
    def reduce_bandwidth_for_users(
        users: list,
        reduction_amount: float,
        min_bandwidth: float,
        cqi_dict: Dict[str, int]
    ) -> Tuple[list, bool]:
        """
        Reduce bandwidth for a list of users to free up network capacity.
        
        Args:
            users: List of user allocation dictionaries
            reduction_amount: Total bandwidth to reduce (MHz)
            min_bandwidth: Minimum acceptable bandwidth per user
            cqi_dict: Dictionary mapping user_id to their CQI
            
        Returns:
            Tuple of (updated_users_list, successfully_reduced_bool)
        """
        if not users or reduction_amount <= 0:
            return users, False
        
        updated_users = []
        total_reduced = 0.0
        
        for user in users:
            if total_reduced >= reduction_amount:
                updated_users.append(user)
                continue
            
            user_id = user.get("user_id")
            current_bw = user.get("bandwidth", 0)
            cqi = cqi_dict.get(user_id, 7)  # Default CQI if not found
            
            # Calculate maximum rate needed
            current_rate = user.get("rate", 0)
            
            # Try to maintain minimum rate
            min_rate = current_rate * 0.8  # Allow 20% rate reduction
            min_bw_needed = ResourceCalculator.adjust_bandwidth(
                current_bw, min_rate, cqi, current_bw
            )
            
            # Can we reduce this user's bandwidth?
            if current_bw - min_bw_needed >= 0.1:  # At least 0.1 MHz reduction
                reduction = min(current_bw - min_bw_needed, reduction_amount - total_reduced)
                new_bw = current_bw - reduction
                
                # Only reduce if still above minimum threshold
                if new_bw >= min_bandwidth:
                    new_rate = ResourceCalculator.calculate_rate_from_cqi(new_bw, cqi)
                    
                    user_copy = user.copy()
                    user_copy["bandwidth"] = round(new_bw, 2)
                    user_copy["rate"] = new_rate
                    updated_users.append(user_copy)
                    
                    total_reduced += reduction
                else:
                    updated_users.append(user)
            else:
                updated_users.append(user)
        
        success = total_reduced >= (reduction_amount * 0.9)  # 90% success threshold
        return updated_users, success
    
    @staticmethod
    def get_slice_constraints(slice_type: SliceType) -> Dict[str, float]:
        """
        Get bandwidth and latency constraints for a slice.
        
        Args:
            slice_type: Target slice (eMBB, URLLC, mMTC)
            
        Returns:
            Dictionary with constraint values
        """
        return ResourceCalculator.SLICE_CONSTRAINTS.get(slice_type, {})
    
    @staticmethod
    def validate_cqi(cqi: int) -> bool:
        """
        Validate if CQI is in acceptable range.
        
        Args:
            cqi: Channel Quality Indicator to validate
            
        Returns:
            True if valid (1-15), False otherwise
        """
        return 1 <= cqi <= 15
