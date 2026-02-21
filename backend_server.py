from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import io
import os
from contextlib import redirect_stdout, redirect_stderr
import pandas as pd
from typing import List, Dict, Any
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

app = FastAPI(title="5G Network Slicing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='network_slicing')

class LogCapture:
    def __init__(self):
        self.logs = []

    def add_log(self, log_type: str, message: str):
        self.logs.append({
            "type": log_type,
            "message": message,
            "time": self._get_current_time()
        })

    def get_logs(self) -> List[Dict[str, str]]:
        return self.logs

    def _get_current_time(self) -> str:
        now = datetime.now()
        return f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"

log_capture = LogCapture()

@app.get("/")
async def root():
    return {"message": "5G Network Slicing API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await asyncio.wait_for(file.read(), timeout=300)
        
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        df = pd.read_csv(temp_file_path)
        
        required_columns = ['RX_ID', 'X', 'Y', 'Z', 'SNR_dB', 'RX_Power_dBm', 'CQI', 'LOS', 'User_Request', 'Request_Label']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            os.remove(temp_file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        return {
            "status": "success",
            "message": "CSV file uploaded successfully",
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns)
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout: Operation took too long to complete")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/process-csv")
async def process_csv(file: UploadFile = File(...)):
    try:
        log_capture = LogCapture()
        
        contents = await asyncio.wait_for(file.read(), timeout=300)
        
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        log_capture.add_log("info", f"开始处理文件: {file.filename}")
        
        df = pd.read_csv(temp_file_path)
        log_capture.add_log("info", f"CSV文件解析成功，共 {len(df)} 条记录")
        
        results = await asyncio.wait_for(process_users_async(df, log_capture, temp_file_path), timeout=600)
        
        os.remove(temp_file_path)
        
        return {
            "status": "success",
            "message": "CSV processing completed",
            "results": results,
            "logs": log_capture.get_logs()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_users_async(df: pd.DataFrame, log_capture: LogCapture, csv_path: str):
    loop = asyncio.get_event_loop()
    
    def process_sync():
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'no_knowledge_base'))
        from no_knowledge_base.WA_DS_V3_NKB import (
            load_user_data_from_csv,
            process_user_request,
            reset_network_state,
            get_current_network_state
        )
        
        reset_network_state()
        
        results = []
        total_users = len(df)
        
        for i, row in df.iterrows():
            user_id = str(row['RX_ID'])
            location = f"({row['X']}, {row['Y']}, {row['Z']})"
            request = row['User_Request']
            cqi = int(row['CQI'])
            ground_truth = row.get('Request_Label', None)
            
            log_capture.add_log("info", f"正在处理用户 {user_id} ({i+1}/{total_users}): {str(request)[:50]}...")
            
            try:
                result = process_user_request(
                    user_id=user_id,
                    location=location,
                    request=request,
                    cqi=cqi,
                    ground_truth=ground_truth
                )
                
                if result.get("allocation_failed", True):
                    log_capture.add_log("error", f"用户 {user_id} 分配失败: {result.get('slice_type', 'Unknown')}")
                else:
                    log_capture.add_log("success", f"用户 {user_id} 分配成功: {result.get('slice_type', 'Unknown')} 切片, 带宽 {result.get('bandwidth', 0)} MHz, 速率 {result.get('rate', 0):.2f} Mbps")
                
                results.append(result)
            except Exception as e:
                log_capture.add_log("error", f"用户 {user_id} 处理出错: {str(e)}")
                results.append({
                    "user_id": user_id,
                    "request": request,
                    "cqi": cqi,
                    "slice_type": "Failed",
                    "allocation_failed": True,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if not r.get("allocation_failed", True))
        failed_count = sum(1 for r in results if r.get("allocation_failed", True))
        
        log_capture.add_log("success", f"所有用户处理完成。成功: {success_count}, 失败: {failed_count}")
        
        return results
    
    return await loop.run_in_executor(executor, process_sync)

@app.get("/results")
async def get_results():
    try:
        result_file = "no_knowledge_base/network_slicing_results_DSv3NKB.csv"
        
        if not os.path.exists(result_file):
            return {
                "status": "no_results",
                "message": "No results available",
                "results": []
            }
        
        df = pd.read_csv(result_file)
        
        results = []
        for _, row in df.iterrows():
            result = {
                "user_id": str(row.get('User ID', '')),
                "request": str(row.get('Request', '')),
                "cqi": int(row.get('CQI', 0)),
                "slice_type": str(row.get('Slice', '')),
                "bandwidth": float(row.get('Bandwidth (MHz)', 0)) if pd.notna(row.get('Bandwidth (MHz)')) else 0,
                "rate": float(row.get('Rate (Mbps)', 0)) if pd.notna(row.get('Rate (Mbps)')) else 0,
                "latency": float(row.get('Latency (ms)', 0)) if pd.notna(row.get('Latency (ms)')) else 0,
                "allocation_failed": row.get('Allocation Status', '') == 'Failed',
                "adjustments_made": row.get('Adjustments Made', '') == 'Yes'
            }
            results.append(result)
        
        return {
            "status": "success",
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset-network")
async def reset_network():
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'no_knowledge_base'))
        from no_knowledge_base.WA_DS_V3_NKB import reset_network_state
        
        reset_network_state()
        
        return {
            "status": "success",
            "message": "Network state reset successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/network-state")
async def get_network_state():
    loop = asyncio.get_event_loop()
    
    def get_state_sync():
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'no_knowledge_base'))
        from no_knowledge_base.WA_DS_V3_NKB import get_current_network_state
        
        return get_current_network_state()
    
    try:
        state = await asyncio.wait_for(loop.run_in_executor(executor, get_state_sync), timeout=30)
        
        return {
            "status": "success",
            "network_state": state
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout: Network state retrieval took too long")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
