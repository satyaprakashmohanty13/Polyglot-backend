from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mitra import process_files, __description__
from args import Setup
import os
import shutil

app = FastAPI()

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create an 'out' directory if it doesn't exist
if not os.path.exists('out'):
    os.makedirs('out')
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.post("/generate")
async def generate_polyglots(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    reverse: bool = Form(False),
    split: bool = Form(False),
    force: bool = Form(False),
    overlap: bool = Form(False),
    pad: int = Form(0)
):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting polyglot generation for files: %s and %s", file1.filename, file2.filename)
        # Save uploaded files to disk
        file1_path = os.path.join("uploads", file1.filename)
        file2_path = os.path.join("uploads", file2.filename)

        with open(file1_path, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)
        with open(file2_path, "wb") as buffer:
            shutil.copyfileobj(file2.file, buffer)

        options = {
            'file1': file1_path,
            'file2': file2_path,
            'reverse': reverse,
            'split': split,
            'force': force,
            'overlap': overlap,
            'pad': pad,
            'outdir': 'out',
            'splitdir': 'out',
            'nofile': True,
            'verbose': True,
        }

        Setup(__description__, config=options)

        with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
            file1_data = f1.read()
            file2_data = f2.read()

        results, generated_files = process_files(
            file1.filename, file1_data,
            file2.filename, file2_data
        )

        # Clean up uploaded files
        os.remove(file1_path)
        os.remove(file2_path)

        import base64
        # Convert generated files to a JSON-serializable format
        response_files = [{"filename": filename, "data": base64.b64encode(data).decode('utf-8')} for filename, data in generated_files]
        logger.info("Successfully generated %d files.", len(response_files))

        return {"results": results, "generated_files": response_files}
    except Exception as e:
        logger.error("An error occurred during polyglot generation: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
