import { useState, useEffect, useRef } from "react"

const surfaceConfig = {
  Clay:  { bg: "bg-amber-700",   text: "text-amber-500",  border: "border-amber-600",  label: "Clay"  },
  Hard:  { bg: "bg-blue-600",    text: "text-blue-400",   border: "border-blue-500",   label: "Hard"  },
  Grass: { bg: "bg-green-700",   text: "text-green-400",  border: "border-green-500",  label: "Grass" },
}

function Avatar({ name, color }) {
  const initials = name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase()
  return (
    <div className={`w-20 h-20 rounded-full flex items-center justify-center text-2xl font-bold text-white ${color} shadow-lg`}>
      {initials || "?"}
    </div>
  )
}

function Autocomplete({ value, onChange, options, placeholder, accentColor }) {
  const [query, setQuery] = useState(value)
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    setQuery(value)
  }, [value])

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  const filtered = query.length < 2 ? [] : options
    .filter(o => o.toLowerCase().includes(query.toLowerCase()))
    .slice(0, 8)

  return (
    <div className="relative" ref={ref}>
      <input
        className={`w-full bg-gray-800 rounded-lg px-3 py-2 text-white text-center placeholder-gray-500 focus:outline-none focus:ring-2 ${accentColor} text-sm`}
        placeholder={placeholder}
        value={query}
        onChange={e => {
          setQuery(e.target.value)
          onChange(e.target.value)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
      />
      {open && filtered.length > 0 && (
        <div className="absolute z-50 w-full bg-gray-800 rounded-lg mt-1 shadow-xl max-h-48 overflow-y-auto">
          {filtered.map(option => (
            <div
              key={option}
              className="px-3 py-2 text-sm text-white hover:bg-gray-700 cursor-pointer"
              onMouseDown={() => {
                setQuery(option)
                onChange(option)
                setOpen(false)
              }}
            >
              {option}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TennisBall() {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <div
          className="w-16 h-16 rounded-full shadow-xl"
          style={{
            animation: "bounce 0.6s infinite alternate cubic-bezier(.4,0,.2,1)",
            background: "radial-gradient(circle at 35% 35%, #faef5d, #b8a800)",
          }}
        />
        <div
          className="w-16 h-3 rounded-full bg-black/20 mx-auto mt-1"
          style={{ animation: "shadow 0.6s infinite alternate cubic-bezier(.4,0,.2,1)" }}
        />
      </div>
      <p className="text-gray-400 mt-6 text-sm tracking-widest uppercase">Analyzing matchup...</p>
      <style>{`
        @keyframes bounce {
          from { transform: translateY(0px); }
          to   { transform: translateY(-48px); }
        }
        @keyframes shadow {
          from { transform: scaleX(1); opacity: 0.3; }
          to   { transform: scaleX(0.5); opacity: 0.1; }
        }
      `}</style>
    </div>
  )
}

function ProbabilityBar({ p1, p2, player1, player2, surface }) {
  const sc = surfaceConfig[surface] || surfaceConfig.Clay
  return (
    <div>
      <div className="flex justify-between items-end mb-3">
        <div>
          <div className="text-3xl font-black">{(p1 * 100).toFixed(1)}%</div>
          <div className="text-sm text-gray-400">{player1}</div>
        </div>
        <div className="text-gray-500 text-sm font-bold uppercase tracking-widest">Win probability</div>
        <div className="text-right">
          <div className="text-3xl font-black">{(p2 * 100).toFixed(1)}%</div>
          <div className="text-sm text-gray-400">{player2}</div>
        </div>
      </div>
      <div className="flex rounded-full overflow-hidden h-5 bg-gray-800">
        <div
          className={`${sc.bg} transition-all duration-1000 ease-out`}
          style={{ width: `${p1 * 100}%` }}
        />
        <div
          className="bg-blue-500 transition-all duration-1000 ease-out"
          style={{ width: `${p2 * 100}%` }}
        />
      </div>
    </div>
  )
}

function StatRow({ label, val1, val2 }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-800">
      <span className="text-xl font-black text-white">{val1}</span>
      <span className="text-xs text-gray-500 uppercase tracking-widest">{label}</span>
      <span className="text-xl font-black text-white">{val2}</span>
    </div>
  )
}

export default function App() {
  const [player1, setPlayer1] = useState("")
  const [player2, setPlayer2] = useState("")
  const [surface, setSurface] = useState("Clay")
  const [tourney, setTourney] = useState("")
  const [round, setRound] = useState("F")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [players, setPlayers] = useState([])
  const [tournaments, setTournaments] = useState([])

  const sc = surfaceConfig[surface] || surfaceConfig.Clay

  useEffect(() => {
    fetch("https://atp-match-predictor-production.up.railway.app/players")
      .then(r => r.json())
      .then(setPlayers)
      .catch(() => {})

    fetch("https://atp-match-predictor-production.up.railway.app/tournaments")
      .then(r => r.json())
      .then(setTournaments)
      .catch(() => {})
  }, [])

  const predict = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch("https://atp-match-predictor-production.up.railway.app/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player1, player2, surface,
          tourney_name: tourney, round,
        }),
      })
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError("Failed to connect to API. Make sure the backend is running.")
    }
    setLoading(false)
  }

  const roundLabels = {
    F: "Final", SF: "Semifinal", QF: "Quarterfinal",
    R16: "R16", R32: "R32", R64: "R64"
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">

      {/* Header */}
      <div className={`${sc.bg} py-4 px-8`}>
        <div className="max-w-2xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-black tracking-tight">ATP MATCH PREDICTOR</h1>
            <p className="text-white/70 text-xs uppercase tracking-widest">ML-powered · AI analysis</p>
          </div>
          <div className="text-white/80 text-sm font-bold uppercase tracking-widest">
            {sc.label}
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto p-6 space-y-4">

        {/* Player vs Player */}
        <div className="grid grid-cols-3 gap-4 items-center">
          <div className="bg-gray-900 rounded-2xl p-4 flex flex-col items-center gap-3">
            <Avatar name={player1} color="bg-amber-700" />
            <Autocomplete
              value={player1}
              onChange={setPlayer1}
              options={players}
              placeholder="Player 1"
              accentColor="focus:ring-amber-600"
            />
          </div>

          <div className="flex flex-col items-center gap-2">
            <div className="text-4xl font-black text-gray-600">VS</div>
            <select
              className="w-full bg-gray-800 rounded-lg px-3 py-2 text-white text-center focus:outline-none text-sm"
              value={surface}
              onChange={e => setSurface(e.target.value)}
            >
              <option>Clay</option>
              <option>Hard</option>
              <option>Grass</option>
            </select>
          </div>

          <div className="bg-gray-900 rounded-2xl p-4 flex flex-col items-center gap-3">
            <Avatar name={player2} color="bg-blue-600" />
            <Autocomplete
              value={player2}
              onChange={setPlayer2}
              options={players}
              placeholder="Player 2"
              accentColor="focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Tournament + Round */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-gray-500 uppercase tracking-widest mb-1 block">Tournament</label>
            <Autocomplete
              value={tourney}
              onChange={setTourney}
              options={tournaments}
              placeholder="Roland Garros"
              accentColor="focus:ring-gray-600"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 uppercase tracking-widest mb-1 block">Round</label>
            <select
              className="w-full bg-gray-900 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-gray-600"
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

        {/* Predict button */}
        <button
          onClick={predict}
          disabled={loading || !player1 || !player2 || !tourney}
          className={`w-full ${sc.bg} hover:opacity-90 disabled:bg-gray-800 disabled:text-gray-600 text-white font-black py-4 rounded-xl text-lg uppercase tracking-widest transition-all`}
        >
          {loading ? "Predicting..." : "Predict Match"}
        </button>

        {/* Error */}
        {error && (
          <div className="bg-red-900/50 border border-red-700 text-red-300 rounded-xl p-4">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && <TennisBall />}

        {/* Results */}
        {result && (
          <div className="space-y-4">

            {/* Winner banner */}
            <div className={`${sc.bg} rounded-2xl p-5 text-center`}>
              <div className="text-xs uppercase tracking-widest text-white/70 mb-1">Predicted winner</div>
              <div className="text-4xl font-black">{result.predicted_winner}</div>
              <div className="text-sm text-white/70 mt-1">
                {tourney} · {roundLabels[round]} · {surface}
              </div>
            </div>

            {/* Probability bar */}
            <div className="bg-gray-900 rounded-2xl p-6">
              <ProbabilityBar
                p1={result.player1_win_probability}
                p2={result.player2_win_probability}
                player1={result.player1}
                player2={result.player2}
                surface={surface}
              />
            </div>

            {/* AI Analysis */}
            <div className="bg-gray-900 rounded-2xl p-6">
              <div className="text-xs uppercase tracking-widest text-gray-500 mb-3">AI Analysis</div>
              <p className="text-gray-200 leading-relaxed text-sm">{result.narrative}</p>
            </div>

            {/* Key Stats */}
            <div className="bg-gray-900 rounded-2xl p-6">
              <div className="text-xs uppercase tracking-widest text-gray-500 mb-3">Key Stats</div>
              <div className="text-xs text-gray-600 flex justify-between mb-2">
                <span>{result.player1}</span>
                <span>{result.player2}</span>
              </div>
              <StatRow
                label="Surface win rate"
                val1={`${(result.features.p1_surface_wr * 100).toFixed(1)}%`}
                val2={`${(result.features.p2_surface_wr * 100).toFixed(1)}%`}
              />
              <StatRow
                label="Recent form"
                val1={`${(result.features.p1_recent_form * 100).toFixed(1)}%`}
                val2={`${(result.features.p2_recent_form * 100).toFixed(1)}%`}
              />
              <StatRow
                label="Ranking"
                val1={`#${result.features.p1_rank}`}
                val2={`#${result.features.p2_rank}`}
              />
              <StatRow
                label="H2H on surface"
                val1={`${(result.features.h2h * 100).toFixed(0)}%`}
                val2={`${((1 - result.features.h2h) * 100).toFixed(0)}%`}
              />
            </div>

          </div>
        )}
      </div>
    </div>
  )
}