from fastapi import FastAPI, HTTPException
from minio import Minio
from minio.deleteobjects import DeleteObject
import os
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(
    title="MinIO API",
    servers=[{"url": "https://hydranoid.site", "description": "Production server"}]
)

# Если планируете обращаться к API из браузера (Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

USERNAME = "python-"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
APP_USER = os.getenv("APP_USER", "python")

client = Minio(
    MINIO_ENDPOINT,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False
)

@app.post("/api/bucket/{uuid}")
def create_bucket(uuid: str):
    bucket_name = f"{USERNAME}{uuid}"
    try:
        if client.bucket_exists(bucket_name):
            return {"status": "exists", "bucket": bucket_name}
        client.make_bucket(bucket_name)
        return {"status": "created", "bucket": bucket_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bucket/{uuid}")
def get_bucket_info(uuid: str):
    bucket_name = f"{USERNAME}{uuid}"
    try:
        if not client.bucket_exists(bucket_name):
            raise HTTPException(status_code=404, detail="Bucket not found")
    
        objects = list(client.list_objects(bucket_name, recursive=True))
        count = len(objects)
        total_size_bytes = sum([obj.size for obj in objects])
        total_size_mb = round(total_size_bytes / (1024 * 1024), 2)
            
        return {
            "bucket": bucket_name,
            "object_count": count,
            "total_size_mb": f"{total_size_mb} Mb",
            "add": "health"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/bucket/{uuid}")
def delete_bucket(uuid: str):
    bucket_name = f"{USERNAME}{uuid}"
    try:
        if not client.bucket_exists(bucket_name):
            raise HTTPException(status_code=404, detail="Bucket not found")

        objects = client.list_objects(bucket_name, recursive=True)
        delete_list = [DeleteObject(obj.object_name) for obj in objects]

        if delete_list:
            errors = client.remove_objects(bucket_name, delete_list)
            for error in errors:
                print(f"Error deleting object: {error}")

        client.remove_bucket(bucket_name)
        
        return {"status": "deleted", "bucket": bucket_name}

    except Exception as e:
        print(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}