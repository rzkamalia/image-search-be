import base64
import datetime
import os
import uvicorn

from database import Database
from fastapi import FastAPI, File, HTTPException, UploadFile, responses
from fastapi.middleware.cors import CORSMiddleware

COLLECTION_NAME = "ImageSearchApp"

app = FastAPI()
db = Database(collection_name = COLLECTION_NAME)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.post("/search")
async def search_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        base64_encoding = base64.b64encode(contents).decode('utf-8')
        
        response = db.query_image(base64_encoding)
        
        results = [r.properties["filename"] for r in response.objects]
        
        # insert log
        db.insert_log(datetime.datetime.now(), file.filename, results)
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@app.get("/image/{filename}")
async def get_image(filename: str):
    image_path = os.path.join("imgs/", filename)
    if os.path.exists(image_path):
        return responses.FileResponse(image_path)
    raise HTTPException(status_code = 404, detail = "Image not found")

if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 5000)