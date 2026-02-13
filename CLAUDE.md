# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **5G Network Slicing Resource Allocation System** that uses LLM-powered intent understanding and graph-based workflow management to allocate network resources across three slice types: eMBB (Enhanced Mobile Broadband), URLLC (Ultra-Reliable Low-Latency Communications), and mMTC (Massive Machine-Type Communications).

The system consists of:
- **Ray Tracing CQI Generator** (`RayTracing_cqi.py`): Simulates wireless channel conditions using OSM building data and generates Channel Quality Indicators (CQI)
- **Knowledge-Base Agent** (`with_knowledge_base/`): Uses an external knowledge base for intent understanding with DeepSeek LLM
- **No-Knowledge-Base Agent** (`no_knowledge_base/`): Pure LLM-based intent understanding without external knowledge

## Key Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the System

**Ray Tracing CQI Generation** (generates input data):
```bash
python RayTracing_cqi.py
```
- Requires OSM building data file at hardcoded path: `F:\code\WirelessAgent_R1\OSM\TX_RT\map_small\export.osm`
- Generates `ray_tracing_results.csv` with user positions, CQI values, and sample requests

**Knowledge-Base Version**:
```bash
python with_knowledge_base/WA_DS_V3_KB.py
```
- Loads user data from `ray_tracing_results.csv`
- Uses knowledge base from `Intent_Understand.txt` for intent classification
- Exports results to `with_knowledge_base/network_slicing_results_DSv3KB.csv`

**No-Knowledge-Base Version**:
```bash
python no_knowledge_base/WA_DS_V3_NKB.py
```
- Same functionality but without external knowledge base
- Results exported to `no_knowledge_base/network_slicing_results_DSv3NKB.csv`

### Processing Single Users

Both KB and NKB versions support processing individual users programmatically:

```python
from with_knowledge_base.WA_DS_V3_KB import process_user_request, reset_network_state

# Reset network state for fresh test
reset_network_state()

# Process a single user
result = process_user_request(
    user_id="1",
    location="(75.64, 182.46, 1.50)",
    request="I need to synchronize distributed financial ledgers instantly",
    cqi=7,
    ground_truth="URLLC"
)
```

## Architecture Overview

### LangGraph Workflow

Both KB and NKB versions use LangGraph for state machine workflow:

1. **initialize**: Receives user request and CQI, sets up state
2. **understand_intent**: Analyzes user request to classify intent
   - KB version: Uses knowledge base + LLM
   - NKB version: Uses LLM only
3. **allocate_slice_type**: Determines eMBB/URLLC/mMTC slice
4. **allocate_resources**: Uses beamforming tool to allocate bandwidth/rate/latency
5. **evaluate_network**: Checks slice capacity, performs dynamic adjustments if needed

### State Definition

```python
class NetworkState(TypedDict):
    user_id: str
    location: str
    request: str
    cqi: int
    history: List[Dict[str, Any]]  # LLM conversation history
    memory: Dict[str, Any]         # Working memory for intermediate results
    step_count: int
    current_step: str
    final_result: Optional[str]
```

### Network Slice Configuration

```python
GLOBAL_NETWORK_STATE = {
    "embb_slice": {
        "total_capacity": 90,  # MHz
        "resource_usage": 0,
        "users": []
    },
    "urllc_slice": {
        "total_capacity": 30,  # MHz
        "resource_usage": 0,
        "users": []
    },
    "mmtc_slice": {
        "total_capacity": 10,  # MHz
        "resource_usage": 0,
        "users": []
    }
}
```

### Key Algorithms

**1. Rate Calculation (Shannon's Formula)**
```python
def calculate_rate_from_cqi(bandwidth, cqi):
    snr = 10 ** (cqi / 10)
    rate = bandwidth * math.log10(1 + snr) * 10
    return round(rate, 2)
```

**2. Dynamic Bandwidth Adjustment**
When slice capacity is exhausted, the system can dynamically reduce bandwidth of existing users:
- Finds users with bandwidth that can be reduced
- Calculates minimum bandwidth needed to maintain minimum rate requirements
- Applies reduction and recalculates rates

**3. Knowledge Base Intent Classification (KB version only)**
Uses pattern matching against a predefined knowledge base (`Intent_Understand.txt`) containing:
- eMBB examples: video streaming, downloads, AR/VR
- URLLC examples: remote control, autonomous driving, real-time monitoring
- mMTC examples: IoT sensors, smart meters, asset tracking

### Data Flow

1. **Input**: User request + CQI (from ray tracing or manual input)
2. **Intent Understanding**: Classify as eMBB/URLLC/mMTC
3. **Slice Selection**: Determine target slice based on intent
4. **Resource Allocation**: Calculate bandwidth, rate, latency using beamforming
5. **Capacity Check**: Verify slice has capacity, trigger adjustments if needed
6. **Output**: Allocation result exported to CSV

### Important File Paths (Hardcoded)

The following paths are hardcoded in the source and may need adjustment:

- `RayTracing_cqi.py`: `F:\code\WirelessAgent_R1\OSM\TX_RT\map_small\export.osm`
- `WA_DS_V3_KB.py`: `F:\code\WirelessAgent_R1\Knowledge_Base\Intent_Understand.txt`

## Common Development Tasks

### Adding a New Test Case

1. Add user request to `Intent_Understand.txt` (for KB version) following the tuple format:
   `("user request text", "eMBB/URLLC/mMTC"),`

2. Run ray tracing or manually create a CSV entry with CQI value

3. Run the appropriate version (KB or NKB) to test

### Modifying Slice Parameters

Edit the `GLOBAL_NETWORK_STATE` dictionary at the top of either KB or NKB file:

```python
GLOBAL_NETWORK_STATE = {
    "embb_slice": {
        "total_capacity": 90,  # Modify this
        # ...
    },
    # ...
}
```

### Running Custom Test Scenarios

Create a Python script that uses the functions directly:

```python
from with_knowledge_base.WA_DS_V3_KB import (
    process_user_request,
    reset_network_state,
    export_results_to_csv
)

# Test multiple users
test_users = [
    {"user_id": "1", "request": "I want to stream 4K video", "cqi": 12, "ground_truth": "eMBB"},
    {"user_id": "2", "request": "I need to control a surgical robot", "cqi": 14, "ground_truth": "URLLC"},
]

results = []
reset_network_state()

for user in test_users:
    result = process_user_request(
        user_id=user["user_id"],
        location="(0, 0, 1.5)",
        request=user["request"],
        cqi=user["cqi"],
        ground_truth=user["ground_truth"]
    )
    results.append(result)

print(f"Processed {len(results)} users")
```

## Testing Considerations

- **API Key**: The system uses a hardcoded DeepSeek API key. For production use, this should be moved to environment variables.
- **File Paths**: Multiple hardcoded Windows paths need adjustment for different environments.
- **CSV Format**: The input CSV must have specific columns: `RX_ID,X,Y,Z,SNR_dB,RX_Power_dBm,CQI,LOS,User_Request,Request_Label`
- **Network State**: Global state persists across function calls - use `reset_network_state()` for clean tests

## Dependencies

Core dependencies (from `requirements.txt`):
- `langgraph`, `langchain-core`, `langchain-openai`: Graph-based LLM workflow
- `openai`: LLM API client
- `pandas`, `tabulate`: Data processing and display
- `numpy`, `scipy`: Numerical computations
- `matplotlib`: Visualization
- `shapely`, `pyproj`: Geospatial processing for ray tracing
