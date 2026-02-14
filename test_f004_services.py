"""
Test script for F004 - Core Service Layer
Validates all service classes work correctly
"""

from app.services import (
    StateManager,
    ResourceCalculator,
    IntentUnderstandingService,
    NetworkSlicingService,
)
from app.models.enums import SliceType, AllocationStatus, IntentType


def test_state_manager():
    """Test StateManager functionality"""
    print("\n" + "="*60)
    print("Testing StateManager")
    print("="*60)
    
    manager = StateManager()
    
    # Test 1: Get current state
    state = manager.get_current_state()
    assert SliceType.EMBB in state, "eMBB slice not found in state"
    assert SliceType.URLLC in state, "URLLC slice not found in state"
    assert SliceType.MMTC in state, "mMTC slice not found in state"
    print("✓ Initial state loaded correctly")
    print(f"  - eMBB capacity: {state[SliceType.EMBB]['total_capacity']} MHz")
    print(f"  - URLLC capacity: {state[SliceType.URLLC]['total_capacity']} MHz")
    print(f"  - mMTC capacity: {state[SliceType.MMTC]['total_capacity']} MHz")
    
    # Test 2: Allocate user
    user_info = {
        "user_id": "test_user_1",
        "bandwidth": 5.0,
        "rate": 25.5,
        "latency": 15.0,
    }
    success = manager.allocate_user(SliceType.EMBB, user_info)
    assert success, "Failed to allocate user"
    print("✓ User allocated to eMBB slice")
    
    # Test 3: Check slice status
    status = manager.get_slice_status(SliceType.EMBB)
    assert status["resource_usage"] == 5.0, "Resource usage not updated correctly"
    assert status["user_count"] == 1, "User count not updated"
    print(f"✓ Slice status updated: {status['user_count']} user, {status['resource_usage']} MHz used")
    
    # Test 4: Check available bandwidth
    available = manager.get_available_bandwidth(SliceType.EMBB)
    assert available == 85.0, "Available bandwidth calculation incorrect"
    print(f"✓ Available bandwidth: {available} MHz")
    
    # Test 5: Deallocate user
    success = manager.deallocate_user(SliceType.EMBB, "test_user_1")
    assert success, "Failed to deallocate user"
    print("✓ User deallocated successfully")
    
    # Test 6: Reset state
    manager.reset_to_initial()
    state = manager.get_current_state()
    assert state[SliceType.EMBB]["resource_usage"] == 0, "State not reset correctly"
    print("✓ State reset successfully")
    
    print("\nStateManager: ALL TESTS PASSED ✓")
    return True


def test_resource_calculator():
    """Test ResourceCalculator functionality"""
    print("\n" + "="*60)
    print("Testing ResourceCalculator")
    print("="*60)
    
    calc = ResourceCalculator()
    
    # Test 1: CQI validation
    assert calc.validate_cqi(7), "CQI 7 should be valid"
    assert not calc.validate_cqi(0), "CQI 0 should be invalid"
    assert not calc.validate_cqi(16), "CQI 16 should be invalid"
    print("✓ CQI validation working")
    
    # Test 2: Rate calculation
    rate = calc.calculate_rate_from_cqi(10.0, 7)
    assert rate > 0, "Rate should be positive"
    print(f"✓ Rate calculation: {10.0} MHz @ CQI=7 → {rate} Mbps")
    
    # Test 3: Latency calculation
    latency = calc.calculate_latency(10.0, 7, SliceType.EMBB)
    assert latency > 0, "Latency should be positive"
    print(f"✓ Latency calculation: {latency} ms for eMBB")
    
    # Test 4: Bandwidth allocation
    alloc = calc.allocate_bandwidth(SliceType.EMBB, 7, 50.0)
    assert alloc["allocated_bandwidth"] > 0, "Bandwidth should be allocated"
    assert alloc["min_bandwidth"] == 6.0, "eMBB min bandwidth should be 6.0"
    print(f"✓ Bandwidth allocation: {alloc['allocated_bandwidth']} MHz for eMBB")
    
    # Test 5: Random CQI generation
    cqi = calc.generate_random_cqi()
    assert 1 <= cqi <= 15, "Random CQI out of range"
    print(f"✓ Random CQI generated: {cqi}")
    
    # Test 6: CQI to SNR conversion
    snr = calc.cqi_to_snr(7)
    assert snr > 0, "SNR should be positive"
    print(f"✓ CQI to SNR conversion: CQI=7 → SNR={snr} dB")
    
    print("\nResourceCalculator: ALL TESTS PASSED ✓")
    return True


def test_intent_understanding_service():
    """Test IntentUnderstandingService functionality"""
    print("\n" + "="*60)
    print("Testing IntentUnderstandingService")
    print("="*60)
    
    service = IntentUnderstandingService(use_knowledge_base=False)
    
    # Test 1: Classify video streaming (eMBB)
    intent, slice_type, reasoning = service.classify_intent("I want to watch 4K video streaming")
    assert slice_type == SliceType.EMBB, f"Expected eMBB, got {slice_type}"
    assert intent == IntentType.BROADBAND, f"Expected BROADBAND intent, got {intent}"
    print(f"✓ Video streaming → {slice_type.value} (intent: {intent.value})")
    
    # Test 2: Classify remote control (URLLC)
    intent, slice_type, reasoning = service.classify_intent("I need to control a surgical robot in real-time")
    assert slice_type == SliceType.URLLC, f"Expected URLLC, got {slice_type}"
    assert intent == IntentType.LOW_LATENCY, f"Expected LOW_LATENCY intent, got {intent}"
    print(f"✓ Remote control → {slice_type.value} (intent: {intent.value})")
    
    # Test 3: Classify IoT monitoring (mMTC)
    intent, slice_type, reasoning = service.classify_intent("Monitor IoT sensors for environmental data")
    assert slice_type == SliceType.MMTC, f"Expected mMTC, got {slice_type}"
    assert intent == IntentType.IOT, f"Expected IOT intent, got {intent}"
    print(f"✓ IoT monitoring → {slice_type.value} (intent: {intent.value})")
    
    # Test 4: Extract entities
    entities = service.extract_entity_from_request("I want to stream 4K video")
    assert "bandwidth_hints" in entities, "Missing bandwidth_hints"
    print(f"✓ Entity extraction: {entities['bandwidth_hints']}")
    
    # Test 5: Get recommendation reasons
    reasons = service.get_slice_recommendation_reasons("Watch HD video")
    assert "selected_slice" in reasons, "Missing selected_slice in reasons"
    assert "confidence" in reasons, "Missing confidence in reasons"
    print(f"✓ Recommendation reasons: {reasons['selected_slice']} (confidence: {reasons['confidence']:.2f})")
    
    print("\nIntentUnderstandingService: ALL TESTS PASSED ✓")
    return True


def test_network_slicing_service():
    """Test NetworkSlicingService functionality"""
    print("\n" + "="*60)
    print("Testing NetworkSlicingService")
    print("="*60)
    
    service = NetworkSlicingService()
    
    # Test 1: Reset network
    success = service.reset_network_state()
    assert success, "Failed to reset network"
    print("✓ Network reset to initial state")
    
    # Test 2: Allocate resources for eMBB request
    result = service.allocate_resources(
        user_id="user_1",
        request="I want to stream 4K video",
        cqi=7
    )
    assert result["status"] == AllocationStatus.SUCCESS.value, "Allocation should succeed"
    assert result["slice_type"] == SliceType.EMBB.value, f"Expected eMBB, got {result['slice_type']}"
    print(f"✓ User 1 allocated to {result['slice_type']}: {result['allocated_bandwidth']} MHz")
    
    # Test 3: Allocate resources for URLLC request
    result = service.allocate_resources(
        user_id="user_2",
        request="I need to control a robot in real-time",
        cqi=12
    )
    assert result["status"] == AllocationStatus.SUCCESS.value, "Allocation should succeed"
    assert result["slice_type"] == SliceType.URLLC.value, f"Expected URLLC, got {result['slice_type']}"
    print(f"✓ User 2 allocated to {result['slice_type']}: {result['allocated_bandwidth']} MHz")
    
    # Test 4: Get network state
    state = service.get_network_state()
    assert SliceType.EMBB in state, "eMBB not in state"
    print(f"✓ Network state retrieved: {state['total_users']} users allocated")
    
    # Test 5: Get network metrics
    metrics = service.get_network_metrics()
    assert "slices" in metrics, "Missing slices in metrics"
    assert metrics["slices"]["eMBB"]["user_count"] == 1, "eMBB user count should be 1"
    print(f"✓ Network metrics: eMBB={metrics['slices']['eMBB']['utilization_rate']:.1%}, "
          f"URLLC={metrics['slices']['URLLC']['utilization_rate']:.1%}")
    
    # Test 6: Classify intent without allocation
    result = service.classify_intent_only("Download a large file")
    assert "intent_type" in result, "Missing intent_type in result"
    assert "recommended_slice" in result, "Missing recommended_slice"
    print(f"✓ Intent classification: {result['intent_type']} → {result['recommended_slice']}")
    
    # Test 7: Get allocation history
    history = service.get_allocation_history()
    assert len(history) >= 2, "Should have at least 2 allocations in history"
    print(f"✓ Allocation history: {len(history)} allocations tracked")
    
    # Test 8: Reset and test batch processing
    service.reset_network_state()
    batch_requests = [
        {"user_id": "batch_1", "request": "Stream 4K video", "cqi": 8},
        {"user_id": "batch_2", "request": "Real-time control", "cqi": 14},
        {"user_id": "batch_3", "request": "IoT monitoring", "cqi": 5},
    ]
    results = service.process_batch_requests(batch_requests)
    assert len(results) == 3, "Should process 3 requests"
    print(f"✓ Batch processing: {len(results)} requests completed")
    for r in results:
        print(f"  - {r['user_id']}: {r['slice_type']} ({r['status']})")
    
    print("\nNetworkSlicingService: ALL TESTS PASSED ✓")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " F004 - Core Service Layer Test Suite ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Run all tests
        test_state_manager()
        test_resource_calculator()
        test_intent_understanding_service()
        test_network_slicing_service()
        
        print("\n" + "╔" + "="*58 + "╗")
        print("║" + " ALL TESTS PASSED ✓ ".center(58) + "║")
        print("╚" + "="*58 + "╝\n")
        
        return True
    
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
