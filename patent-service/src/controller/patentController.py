import os.path

from fastapi import FastAPI, Request, Response, HTTPException, Form
from pydantic import BaseModel
import uvicorn

import src.constants as const


app = FastAPI()


@app.get("/patent/summary/{patent_name}")
def get_patent_summary(patent_name: str):
    path = const.OUTPUT_DIR + "/summary/" + patent_name + ".txt"
    if os.path.exists(path):
        with open(path, "r") as f:
            return Response(content=f.read(), media_type="text/plain")
    else:
        return Response(content="Not found", media_type="text/plain")


@app.get("/patent/audio/{patent_name}")
def get_patent_audio(patent_name: str):
    path = const.OUTPUT_DIR + "/audio/" + patent_name + ".mp3"
    if os.path.exists(path):
        return Response(content=path, media_type="text/plain")
    else:
        return Response(content="Not found", media_type="text/plain")


@app.get("/patent/podcast/{patent_name}")
def get_patent_podcast(patent_name: str):
    path = const.OUTPUT_DIR + "/podcast/" + patent_name + ".wav"
    if os.path.exists(path):
        return Response(content=path, media_type="text/plain")
    else:
        return Response(content="Not found", media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")