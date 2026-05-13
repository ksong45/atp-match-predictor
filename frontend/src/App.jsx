import { useState } from "react"

export default function App() {
  const [player1, setPlayer1] = useState("")
  const [player2, setPlayer2] = useState("")
  const [surface, setSurface] = useState("Clay")
  const [tourney, setTourney] = useState("")
  const [round, setRound] = useState("F")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const predict = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player1,
          player2,
          surface,
          tourney_name: tourney,
          round,
        }),
      })
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError("Failed to connect to API. Make sure the backend is running.")
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="mb-10 text-center">
          <h1 className="text-4xl font-bold mb-2">ATP Match Predictor</h1>
          <p className="text-gray-400">ML-powered predictions with AI analysis</p>
        </div>

        {/* Input form */}
        <div className="bg-gray-900 rounded-2xl p-6 mb-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-400 mb-1 block">Player 1</label>
              <input
                className="w-full bg-gray-800 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Carlos Alcaraz"
                value={player1}
                onChange={e => setPlayer1(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm text-gray-400 mb-1 block">Player 2</label>
              <input
                className="w-full bg-gray-800 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Jannik Sinner"
                value={player2}
                onChange={e => setPlayer2(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-400 mb-1 block">Surface</label>
              <select
                className="w-full bg-gray-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                value={surface}
                onChange={e => setSurface(e.target.value)}
              >
                <option>Clay</option>
                <option>Hard</option>
                <option>Grass</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-400 mb-1 block">Tournament</label>
              <input
                className="w-full bg-gray-800 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Roland Garros"
                value={tourney}
                onChange={e => setTourney(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm text-gray-400 mb-1 block">Round</label>
              <select
                className="w-full bg-gray-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                value={round}
                onChange={e => setRound(e.target.value)}
              >
                <option value="F">Final</option>
                <option value="SF">Semifinal</option>
                <option value="QF">Quarterfinal</option>
                <option value="R16">Round of 16</option>
                <option value="R32">Round of 32</option>
                <option value="R64">Round of 64</option>
              </select>
            </div>
          </div>

          <button
            onClick={predict}
            disabled={loading || !player1 || !player2 || !tourney}
            className="w-full bg-green-500 hover:bg-green-400 disabled:bg-gray-700 disabled:text-gray-500 text-black font-bold py-3 rounded-lg transition-colors"
          >
            {loading ? "Predicting..." : "Predict Match"}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-900 text-red-200 rounded-xl p-4 mb-6">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-4">

            {/* Win probabilities */}
            <div className="bg-gray-900 rounded-2xl p-6">
              <h2 className="text-lg font-semibold mb-4 text-gray-300">Prediction</h2>
              <div className="flex justify-between items-center mb-3">
                <span className="font-bold text-lg">{result.player1}</span>
                <span className="font-bold text-lg">{result.player2}</span>
              </div>
              <div className="flex rounded-full overflow-hidden h-4 mb-3">
                <div
                  className="bg-green-500 transition-all"
                  style={{ width: `${result.player1_win_probability * 100}%` }}
                />
                <div
                  className="bg-blue-500 transition-all"
                  style={{ width: `${result.player2_win_probability * 100}%` }}
                />
              </div>
              <div className="flex justify-between text-sm text-gray-400">
                <span>{(result.player1_win_probability * 100).toFixed(1)}%</span>
                <span className="text-white font-bold">
                  {result.predicted_winner} wins
                </span>
                <span>{(result.player2_win_probability * 100).toFixed(1)}%</span>
              </div>
            </div>

            {/* AI Narrative */}
            <div className="bg-gray-900 rounded-2xl p-6">
              <h2 className="text-lg font-semibold mb-3 text-gray-300">AI Analysis</h2>
              <p className="text-gray-200 leading-relaxed">{result.narrative}</p>
            </div>

            {/* Key stats */}
            <div className="bg-gray-900 rounded-2xl p-6">
              <h2 className="text-lg font-semibold mb-4 text-gray-300">Key Stats</h2>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Surface win rate</span>
                  <span>{(result.features.p1_surface_wr * 100).toFixed(1)}% vs {(result.features.p2_surface_wr * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Recent form</span>
                  <span>{(result.features.p1_recent_form * 100).toFixed(1)}% vs {(result.features.p2_recent_form * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Ranking</span>
                  <span>#{result.features.p1_rank} vs #{result.features.p2_rank}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">H2H on surface</span>
                  <span>{(result.features.h2h * 100).toFixed(0)}% / {((1 - result.features.h2h) * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  )
}