import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def compute_elo(df, k=32, base=1500):
    """Compute Elo ratings chronologically"""
    print("Computing Elo ratings...")
    elo = {}
    elo_before_match = []

    for _, row in df.iterrows():
        winner = row['winner_name']
        loser = row['loser_name']

        w_elo = elo.get(winner, base)
        l_elo = elo.get(loser, base)

        w_exp = 1 / (1 + 10 ** ((l_elo - w_elo) / 400))
        l_exp = 1 - w_exp

        elo_before_match.append({
            'winner_elo': w_elo,
            'loser_elo': l_elo,
            'winner_elo_exp': w_exp
        })

        elo[winner] = w_elo + k * (1 - w_exp)
        elo[loser] = l_elo + k * (0 - l_exp)

    return pd.DataFrame(elo_before_match)

def get_training_data():
    query = text("""
        SELECT 
            winner_name, loser_name, surface, tourney_name,
            winner_rank, loser_rank, winner_rank_points, loser_rank_points,
            winner_age, loser_age, tourney_date, tourney_level, round,
            w_ace, w_df, "w_1stIn", "w_1stWon", "w_2ndWon", "w_bpSaved", "w_bpFaced",
            l_ace, l_df, "l_1stIn", "l_1stWon", "l_2ndWon", "l_bpSaved", "l_bpFaced",
            minutes, best_of
        FROM matches
        WHERE winner_rank IS NOT NULL 
        AND loser_rank IS NOT NULL
        AND tourney_date >= '19900101'
        ORDER BY tourney_date ASC
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    print(f"Pulled {len(df)} matches for training")
    return df

def encode_round(round_str):
    round_map = {
        'R128': 1, 'R64': 2, 'R32': 3, 'R16': 4,
        'QF': 5, 'SF': 6, 'F': 7, 'RR': 3
    }
    return round_map.get(round_str, 3)

def engineer_features(df, elo_df):
    rows = []
    player_match_history = {}
    player_serve_history = {}

    print("Engineering features...")

    for idx, row in df.iterrows():
        winner = row['winner_name']
        loser = row['loser_name']
        surface = row['surface']
        date = row['tourney_date']

        for p in [winner, loser]:
            if p not in player_match_history:
                player_match_history[p] = []
            if p not in player_serve_history:
                player_serve_history[p] = []

        def get_stats(player, opponent, surf):
            history = player_match_history[player]
            serve_history = player_serve_history[player]

            if not history:
                return {
                    'surface_wr': 0.5,
                    'recent_form': 0.5,
                    'h2h': 0.5,
                    'avg_ace_rate': 0.0,
                    'avg_1st_serve': 0.0,
                    'avg_1st_won': 0.0,
                    'avg_bp_saved': 0.0,
                }

            surf_matches = [m for m in history if m['surface'] == surf][-50:]
            surf_wr = (sum(1 for m in surf_matches if m['won']) / len(surf_matches)
                      if surf_matches else 0.5)

            recent = history[-15:]
            recent_form = sum(1 for m in recent if m['won']) / len(recent)

            h2h_matches = [m for m in history if m['opponent'] == opponent]
            h2h = (sum(1 for m in h2h_matches if m['won']) / len(h2h_matches)
                  if h2h_matches else 0.5)

            recent_serve = serve_history[-20:]
            avg_ace_rate = np.mean([s['ace_rate'] for s in recent_serve]) if recent_serve else 0.0
            avg_1st_serve = np.mean([s['first_serve'] for s in recent_serve]) if recent_serve else 0.0
            avg_1st_won = np.mean([s['first_won'] for s in recent_serve]) if recent_serve else 0.0
            avg_bp_saved = np.mean([s['bp_saved'] for s in recent_serve]) if recent_serve else 0.0

            return {
                'surface_wr': surf_wr,
                'recent_form': recent_form,
                'h2h': h2h,
                'avg_ace_rate': avg_ace_rate,
                'avg_1st_serve': avg_1st_serve,
                'avg_1st_won': avg_1st_won,
                'avg_bp_saved': avg_bp_saved,
            }

        w_stats = get_stats(winner, loser, surface)
        l_stats = get_stats(loser, winner, surface)

        w_elo = elo_df.iloc[idx]['winner_elo']
        l_elo = elo_df.iloc[idx]['loser_elo']

        if np.random.random() > 0.5:
            p1, p2 = winner, loser
            p1_stats, p2_stats = w_stats, l_stats
            p1_rank = row['winner_rank']
            p2_rank = row['loser_rank']
            p1_elo, p2_elo = w_elo, l_elo
            p1_age = row['winner_age']
            p2_age = row['loser_age']
            label = 1
        else:
            p1, p2 = loser, winner
            p1_stats, p2_stats = l_stats, w_stats
            p1_rank = row['loser_rank']
            p2_rank = row['winner_rank']
            p1_elo, p2_elo = l_elo, w_elo
            p1_age = row['loser_age']
            p2_age = row['winner_age']
            label = 0

        feature_row = {
            'p1_surface_wr':   p1_stats['surface_wr'],
            'p1_recent_form':  p1_stats['recent_form'],
            'p1_rank':         p1_rank,
            'p1_elo':          p1_elo,
            'p1_age':          p1_age if pd.notna(p1_age) else 25.0,
            'p1_ace_rate':     p1_stats['avg_ace_rate'],
            'p1_1st_serve':    p1_stats['avg_1st_serve'],
            'p1_1st_won':      p1_stats['avg_1st_won'],
            'p1_bp_saved':     p1_stats['avg_bp_saved'],
            'p2_surface_wr':   p2_stats['surface_wr'],
            'p2_recent_form':  p2_stats['recent_form'],
            'p2_rank':         p2_rank,
            'p2_elo':          p2_elo,
            'p2_age':          p2_age if pd.notna(p2_age) else 25.0,
            'p2_ace_rate':     p2_stats['avg_ace_rate'],
            'p2_1st_serve':    p2_stats['avg_1st_serve'],
            'p2_1st_won':      p2_stats['avg_1st_won'],
            'p2_bp_saved':     p2_stats['avg_bp_saved'],
            'h2h':             p1_stats['h2h'],
            'rank_diff':       p2_rank - p1_rank,
            'elo_diff':        p1_elo - p2_elo,
            'age_diff':        p1_age - p2_age if pd.notna(p1_age) and pd.notna(p2_age) else 0,
            'surface_clay':    1 if surface == 'Clay' else 0,
            'surface_grass':   1 if surface == 'Grass' else 0,
            'surface_hard':    1 if surface == 'Hard' else 0,
            'is_grand_slam':   1 if row['tourney_level'] == 'G' else 0,
            'round_num':       encode_round(row['round']),
            'best_of':         row['best_of'] if pd.notna(row['best_of']) else 3,
            'label':           label
        }
        rows.append(feature_row)

        player_match_history[winner].append({
            'opponent': loser, 'surface': surface, 'won': True, 'date': date
        })
        player_match_history[loser].append({
            'opponent': winner, 'surface': surface, 'won': False, 'date': date
        })

        w_1stIn = row.get('w_1stIn')
        w_1stWon = row.get('w_1stWon')
        w_bpSaved = row.get('w_bpSaved')
        w_bpFaced = row.get('w_bpFaced')
        w_ace = row.get('w_ace')
        w_svpt = row.get('w_svpt')

        if w_svpt and pd.notna(w_svpt) and w_svpt > 0:
            player_serve_history[winner].append({
                'ace_rate':    w_ace / w_svpt if pd.notna(w_ace) else 0,
                'first_serve': w_1stIn / w_svpt if pd.notna(w_1stIn) else 0,
                'first_won':   w_1stWon / w_1stIn if pd.notna(w_1stWon) and pd.notna(w_1stIn) and w_1stIn > 0 else 0,
                'bp_saved':    w_bpSaved / w_bpFaced if pd.notna(w_bpSaved) and pd.notna(w_bpFaced) and w_bpFaced > 0 else 0,
            })

        if idx % 5000 == 0:
            print(f"Processed {idx} matches...")

    return pd.DataFrame(rows)

def train_model():
    df = get_training_data()
    elo_df = compute_elo(df)
    features_df = engineer_features(df, elo_df)

    X = features_df.drop('label', axis=1)
    y = features_df['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    print("Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel accuracy: {accuracy:.3f}")

    os.makedirs("backend/models", exist_ok=True)
    joblib.dump(model, "backend/models/match_predictor.pkl")
    print("Model saved to backend/models/match_predictor.pkl")

    importance = pd.Series(
        model.feature_importances_,
        index=X.columns
    ).sort_values(ascending=False)
    print("\nFeature importance:")
    print(importance)

if __name__ == "__main__":
    train_model()