import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_narrative(player1, player2, surface, tourney_name, round, features, prediction):
    """Generate a sports reporter blurb for a matchup"""

    prompt = f"""You are an expert tennis analyst and sports journalist. 
    
Here is data for an upcoming match:

Match: {player1} vs {player2}
Tournament: {tourney_name} ({round})
Surface: {surface}

Statistical breakdown:
- {player1} surface win rate: {features['p1_surface_wr']:.1%}
- {player2} surface win rate: {features['p2_surface_wr']:.1%}
- {player1} recent form (last 15): {features['p1_recent_form']:.1%}
- {player2} recent form (last 15): {features['p2_recent_form']:.1%}
- {player1} current ranking: #{int(features['p1_rank'])}
- {player2} current ranking: #{int(features['p2_rank'])}
- Head to head on {surface}: {player1} leads {features['h2h']:.0%} to {1-features['h2h']:.0%}
- Predicted winner: {prediction['predicted_winner']} ({max(prediction['player1_win_probability'], prediction['player2_win_probability']):.0%} probability)

Write a 3-4 sentence match preview in the style of a seasoned ESPN analyst. Cover:
1. The key storyline of this matchup
2. What each player needs to do to win
3. Your prediction and why

Be specific, confident, and engaging. Use the statistics to support your analysis."""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

if __name__ == "__main__":
    # Quick test
    features = {
        'p1_surface_wr': 0.907,
        'p2_surface_wr': 0.900,
        'p1_recent_form': 0.733,
        'p2_recent_form': 1.0,
        'p1_rank': 2,
        'p2_rank': 1,
        'h2h': 0.6,
    }
    prediction = {
        'predicted_winner': 'Jannik Sinner',
        'player1_win_probability': 0.432,
        'player2_win_probability': 0.568,
    }
    blurb = generate_narrative(
        "Carlos Alcaraz", "Jannik Sinner",
        "Clay", "Roland Garros", "F",
        features, prediction
    )
    print(blurb)