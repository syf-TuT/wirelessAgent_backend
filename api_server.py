from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import sys
import os
from typing import List, Dict, Any
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from no_knowledge_base.WA_DS_V3_NKB import (
    load_user_data_from_csv as load_user_data_from_csv_nkb,
    process_user_request as process_user_request_nkb,
    reset_network_state as reset_network_state_nkb,
    export_results_to_csv as export_results_to_csv_nkb
)

from with_knowledge_base.WA_DS_V3_KB import (
    load_user_data_from_csv as load_user_data_from_csv_kb,
    process_user_request as process_user_request_kb,
    reset_network_state as reset_network_state_kb,
    export_results_to_csv as export_results_to_csv_kb
)

app = FastAPI(title="5G Network Slicing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "5G Network Slicing API", "version": "1.0.0"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        users = load_user_data_from_csv_nkb(temp_file_path)
        
        os.remove(temp_file_path)
        
        return {
            "success": True,
            "message": f"Successfully loaded {len(users)} users",
            "users_count": len(users),
            "users": users[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-csv")
async def process_csv(
    file: UploadFile = File(...),
    use_knowledge_base: bool = Form(False)
):
    try:
        contents = await file.read()
        
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        if use_knowledge_base:
            users = load_user_data_from_csv_kb(temp_file_path)
            reset_network_state_kb()
        else:
            users = load_user_data_from_csv_nkb(temp_file_path)
            reset_network_state_nkb()
        
        results = []
        for user in users:
            if use_knowledge_base:
                result = process_user_request_kb(
                    user_id=user['user_id'],
                    location=user['location'],
                    request=user['request'],
                    cqi=user['cqi'],
                    ground_truth=user.get('ground_truth')
                )
            else:
                result = process_user_request_nkb(
                    user_id=user['user_id'],
                    location=user['location'],
                    request=user['request'],
                    cqi=user['cqi'],
                    ground_truth=user.get('ground_truth')
                )
            results.append(result)
        
        os.remove(temp_file_path)
        
        return {
            "success": True,
            "message": f"Successfully processed {len(results)} users",
            "total_users": len(results),
            "results": results,
            "use_knowledge_base": use_knowledge_base
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results():
    try:
        result_file = "network_slicing_results_DSv3NKB.csv"
        if os.path.exists(result_file):
            df = pd.read_csv(result_file)
            return {
                "success": True,
                "results": df.to_dict(orient='records')
            }
        else:
            return {
                "success": False,
                "message": "No results found"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
