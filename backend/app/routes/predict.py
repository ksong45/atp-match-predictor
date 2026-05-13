from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from backend.app.services.features import compute_features

router = APIRouter()
model = joblib.load("backend/models/match_predictor.pkl")

class PredictRequest(BaseModel):
    player1: str
    player2: str
    surface: str
    tourney_name: str
    round: str

@router.post("/predict")
def predict(request: PredictRequest):
    features = compute_features(
        request.player1,
        request.player2,
        request.surface,
        request.tourney_name,
        request.round
    )

    feature_order = [
        'p1_surface_wr', 'p1_recent_form', 'p1_rank', 'p1_elo',
        'p1_age', 'p1_ace_rate', 'p1_1st_serve', 'p1_1st_won',
        'p1_bp_saved', 'p2_surface_wr', 'p2_recent_form', 'p2_rank',
        'p2_elo', 'p2_age', 'p2_ace_rate', 'p2_1st_serve', 'p2_1st_won',
        'p2_bp_saved', 'h2h', 'rank_diff', 'elo_diff', 'age_diff',
        'surface_clay', 'surface_grass', 'surface_hard',
        'is_grand_slam', 'round_num', 'best_of'
    ]

    X = pd.DataFrame([features])[feature_order]
    prob = model.predict_proba(X)[0]

    prediction = {
        "player1": request.player1,
        "player2": request.player2,
        "player1_win_probability": round(float(prob[1]), 3),
        "player2_win_probability": round(float(prob[0]), 3),
        "predicted_winner": request.player1 if prob[1] > 0.5 else request.player2,
    }

    from backend.app.services.narrative import generate_narrative
    narrative = generate_narrative(
        request.player1, request.player2,
        request.surface, request.tourney_name,
        request.round, features, prediction
    )

    return {**prediction, "narrative": narrative, "features": features}