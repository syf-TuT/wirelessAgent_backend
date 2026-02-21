from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import sys
import os
from typing import List, Dict, Any
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from no_knowledge_base.WA_DS_V3_NKB import (
    load_user_data_from_csv,
    process_user_request,
    reset_network_state,
    export_results_to_csv
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
        
        users = load_user_data_from_csv(temp_file_path)
        
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
async def process_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        users = load_user_data_from_csv(temp_file_path)
        
        reset_network_state()
        
        results = []
        for user in users:
            result = process_user_request(
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
            "results": results
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
