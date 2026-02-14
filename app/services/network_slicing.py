"""
NetworkSlicingService - Main service for network resource allocation and slicing
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from app.models.enums import SliceType, AllocationStatus, IntentType
from app.services.state_manager import StateManager
from app.services.resource_calculator import ResourceCalculator
from app.services.intent_understanding import IntentUnderstandingService


class NetworkSlicingService:
    """
    Main service orchestrating network resource allocation across slices.
    
    Integrates intent understanding, resource calculation, and state management
    to perform intelligent network slicing and resource allocation.
    """
    
    def __init__(
        self,
        state_manager: Optional[StateManager] = None,
        intent_service: Optional[IntentUnderstandingService] = None,
        use_knowledge_base: bool = False,
        knowledge_base_content: Optional[str] = None
    ):
        """
        Initialize NetworkSlicingService with required components.
        
        Args:
            state_manager: StateManager instance (creates new if None)
            intent_service: IntentUnderstandingService instance (creates new if None)
            use_knowledge_base: Enable knowledge-base intent classification
            knowledge_base_content: Knowledge base file content for intent classification
        """
        self.state_manager = state_manager or StateManager()
        self.intent_service = intent_service or IntentUnderstandingService(
            use_knowledge_base=use_knowledge_base,
            knowledge_base_content=knowledge_base_content
        )
        self.resource_calculator = ResourceCalculator()
        
        # Track allocation history
        self.allocation_history: List[Dict[str, Any]] = []
    
    def allocate_resources(
        self,
        user_id: str,
        request: str,
        location: Optional[str] = None,
        cqi: Optional[int] = None,
        ground_truth: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user request and allocate network resources.
        
        This is the main entry point for resource allocation combining:
        1. Intent understanding
        2. Slice selection
        3. Resource calculation
        4. Capacity checking and load balancing
        
        Args:
            user_id: Unique user identifier
            request: User's natural language request
            location: User's geographic location (optional)
            cqi: Channel Quality Indicator 1-15 (generated if not provided)
            ground_truth: Ground truth slice label for evaluation (optional)
            
        Returns:
            Dictionary containing allocation results with:
            {
                'allocation_id': str,
                'user_id': str,
                'status': AllocationStatus,
                'slice_type': SliceType,
                'allocated_bandwidth': float,
                'transmission_rate': float,
                'latency': float,
                'reasoning': List[str],
                'timestamp': str,
            }
        """
        # Generate CQI if not provided
        if cqi is None:
            cqi = self.resource_calculator.generate_random_cqi()
        
        # Validate CQI
        if not self.resource_calculator.validate_cqi(cqi):
            cqi = max(1, min(15, cqi))
        
        allocation_id = f"alloc_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        reasoning = []
        
        try:
            # Step 1: Understand intent
            intent, initial_slice, intent_reasoning = self.intent_service.classify_intent(request)
            reasoning.extend(intent_reasoning)
            
            # Step 2: Check capacity and select final slice
            final_slice, rebalance_reason = self._select_slice_with_balancing(
                initial_slice, cqi
            )
            if rebalance_reason:
                reasoning.append(rebalance_reason)
            
            # Step 3: Allocate resources
            allocation_info = self._allocate_to_slice(
                user_id, final_slice, cqi, request
            )
            
            if not allocation_info["success"]:
                # Try alternative slice
                alt_slice = self.state_manager.get_least_utilized_slice()
                if alt_slice != final_slice:
                    reasoning.append(f"Primary slice {final_slice} full, trying {alt_slice}")
                    allocation_info = self._allocate_to_slice(
                        user_id, alt_slice, cqi, request
                    )
                    final_slice = alt_slice
            
            # Build response
            if allocation_info["success"]:
                status = AllocationStatus.SUCCESS
                allocated_bw = allocation_info["bandwidth"]
                rate = allocation_info["rate"]
                latency = allocation_info["latency"]
            else:
                status = AllocationStatus.FAILED
                allocated_bw = 0.0
                rate = 0.0
                latency = 0.0
                reasoning.append("Insufficient capacity in all slices")
            
            result = {
                "allocation_id": allocation_id,
                "user_id": user_id,
                "request": request,
                "status": status.value,
                "slice_type": final_slice.value,
                "intent_type": intent.value,
                "allocated_bandwidth": allocated_bw,
                "transmission_rate": rate,
                "latency": latency,
                "cqi": cqi,
                "location": location or "Unknown",
                "ground_truth": ground_truth,
                "reasoning": reasoning,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            
            # Add to history
            self.allocation_history.append(result)
            
            return result
        
        except Exception as e:
            return {
                "allocation_id": allocation_id,
                "user_id": user_id,
                "request": request,
                "status": AllocationStatus.FAILED.value,
                "error": str(e),
                "reasoning": reasoning + [f"Error: {str(e)}"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
    
    def _select_slice_with_balancing(
        self,
        preferred_slice: SliceType,
        cqi: int
    ) -> Tuple[SliceType, Optional[str]]:
        """
        Select final slice considering workload balancing.
        
        Args:
            preferred_slice: Initially selected slice from intent
            cqi: Channel Quality Indicator
            
        Returns:
            Tuple of (final_slice, rebalance_reason)
        """
        # Check if preferred slice has capacity
        constraints = self.resource_calculator.get_slice_constraints(preferred_slice)
        min_bw = constraints.get("min_bandwidth", 1.0)
        
        if self.state_manager.can_allocate(preferred_slice, min_bw):
            return preferred_slice, None
        
        # Need to rebalance - find least utilized slice
        utilization_rates = self.state_manager.get_utilization_rates()
        least_utilized = min(utilization_rates.keys(), key=lambda k: utilization_rates[k])
        
        rebalance_reason = f"Rebalancing: {preferred_slice} full ({utilization_rates[preferred_slice]:.1%}), using {least_utilized} ({utilization_rates[least_utilized]:.1%})"
        
        return least_utilized, rebalance_reason
    
    def _allocate_to_slice(
        self,
        user_id: str,
        slice_type: SliceType,
        cqi: int,
        request: str
    ) -> Dict[str, Any]:
        """
        Allocate bandwidth and resources to a specific slice.
        
        Args:
            user_id: User identifier
            slice_type: Target slice
            cqi: Channel Quality Indicator
            request: User request (for analysis)
            
        Returns:
            Dictionary with allocation details
        """
        available = self.state_manager.get_available_bandwidth(slice_type)
        
        # Calculate bandwidth allocation
        allocation = self.resource_calculator.allocate_bandwidth(
            slice_type, cqi, available
        )
        
        allocated_bw = allocation["allocated_bandwidth"]
        
        if allocated_bw <= 0:
            return {"success": False}
        
        # Calculate rate and latency
        rate = self.resource_calculator.calculate_rate_from_cqi(allocated_bw, cqi)
        latency = self.resource_calculator.calculate_latency(allocated_bw, cqi, slice_type)
        
        # Prepare user info
        user_info = {
            "user_id": user_id,
            "bandwidth": allocated_bw,
            "rate": rate,
            "latency": latency,
            "cqi": cqi,
            "request": request,
            "allocation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Try to allocate
        success = self.state_manager.allocate_user(slice_type, user_info)
        
        return {
            "success": success,
            "bandwidth": allocated_bw if success else 0.0,
            "rate": rate if success else 0.0,
            "latency": latency if success else 0.0,
        }
    
    def deallocate_user(self, user_id: str, slice_type: SliceType) -> bool:
        """
        Remove a user from a slice.
        
        Args:
            user_id: User identifier to deallocate
            slice_type: Source slice
            
        Returns:
            True if successful
        """
        return self.state_manager.deallocate_user(slice_type, user_id)
    
    def get_network_state(self) -> Dict[str, Any]:
        """
        Get current complete network state.
        
        Returns:
            Dictionary with all slice statuses
        """
        return self.state_manager.get_current_state()
    
    def get_slice_status(self, slice_type: SliceType) -> Dict[str, Any]:
        """
        Get status of a specific slice.
        
        Args:
            slice_type: Slice to query
            
        Returns:
            Detailed slice status
        """
        return self.state_manager.get_slice_status(slice_type)
    
    def reset_network_state(self) -> bool:
        """
        Reset network to initial state.
        
        Returns:
            True if successful
        """
        return self.state_manager.reset_to_initial()
    
    def get_allocation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent allocation history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of allocation results
        """
        return self.allocation_history[-limit:]
    
    def classify_intent_only(self, request: str) -> Dict[str, Any]:
        """
        Classify intent without performing allocation.
        
        Args:
            request: User's natural language request
            
        Returns:
            Dictionary with intent classification and reasoning
        """
        intent, slice_type, reasoning = self.intent_service.classify_intent(request)
        
        return {
            "request": request,
            "intent_type": intent.value,
            "recommended_slice": slice_type.value,
            "reasoning": reasoning,
            "confidence": self.intent_service._calculate_confidence(intent, request),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def get_network_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive network metrics.
        
        Returns:
            Dictionary with various network metrics
        """
        state = self.state_manager.get_current_state()
        rates = self.state_manager.get_utilization_rates()
        
        metrics = {
            "total_users": state.get("total_users", 0),
            "timestamp": state.get("timestamp"),
            "slices": {
                SliceType.EMBB.value: {
                    "total_capacity": state[SliceType.EMBB]["total_capacity"],
                    "resource_usage": state[SliceType.EMBB]["resource_usage"],
                    "utilization_rate": rates[SliceType.EMBB],
                    "user_count": len(state[SliceType.EMBB]["users"]),
                    "total_transmission_rate": state[SliceType.EMBB]["total_transmission_rate"],
                },
                SliceType.URLLC.value: {
                    "total_capacity": state[SliceType.URLLC]["total_capacity"],
                    "resource_usage": state[SliceType.URLLC]["resource_usage"],
                    "utilization_rate": rates[SliceType.URLLC],
                    "user_count": len(state[SliceType.URLLC]["users"]),
                    "total_transmission_rate": state[SliceType.URLLC]["total_transmission_rate"],
                },
                SliceType.MMTC.value: {
                    "total_capacity": state[SliceType.MMTC]["total_capacity"],
                    "resource_usage": state[SliceType.MMTC]["resource_usage"],
                    "utilization_rate": rates[SliceType.MMTC],
                    "user_count": len(state[SliceType.MMTC]["users"]),
                    "total_transmission_rate": state[SliceType.MMTC]["total_transmission_rate"],
                },
            }
        }
        
        return metrics
    
    def process_batch_requests(
        self,
        requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process multiple requests sequentially.
        
        Args:
            requests: List of request dictionaries with user_id, request, etc.
            
        Returns:
            List of allocation results
        """
        results = []
        for req in requests:
            result = self.allocate_resources(
                user_id=req.get("user_id", f"user_{len(results)}"),
                request=req.get("request", ""),
                location=req.get("location"),
                cqi=req.get("cqi"),
                ground_truth=req.get("ground_truth"),
            )
            results.append(result)
        
        return results
