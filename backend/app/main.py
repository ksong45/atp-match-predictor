from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.predict import router

app = FastAPI(title="ATP Match Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "ATP Match Predictor API"}