import { useEffect, useMemo, useState } from 'react'
import './App.css'
import { ApiError, apiRequest, readSession, saveSession, clearSession } from './api'

function App() {
  const [credentials, setCredentials] = useState({
    user_name: '',
    password: '',
    name: '',
  })
  const [session, setSession] = useState(() => readSession())
  const [games, setGames] = useState([])
  const [game, setGame] = useState(null)
  const [statusText, setStatusText] = useState('Melde dich an oder registriere dich, um zu starten.')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState({ text: '', type: '' })

  const board = game?.board ?? Array(9).fill(null)
  const isOngoing = game?.status === 'ongoing'

  useEffect(() => {
    if (session.token) {
      saveSession(session)
    } else {
      clearSession()
    }
  }, [session])

  useEffect(() => {
    if (!session.token) {
      setGames([])
      setGame(null)
      return
    }
    hydrateState()
  }, [session.token])

  const authHeaders = useMemo(() => {
    if (!session.token) {
      return {}
    }
    return { Authorization: `Bearer ${session.token}` }
  }, [session.token])

  async function hydrateState() {
    try {
      setBusy(true)
      const allGames = await apiRequest('/games', { headers: authHeaders })
      setGames(allGames)
      if (session.gameId) {
        const loadedGame = await apiRequest(`/games/${session.gameId}`, {
          headers: authHeaders,
        })
        setGame(loadedGame)
        setStatusText(formatHeadline(loadedGame))
      } else {
        setStatusText('Bereit fuer ein neues Spiel.')
      }
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        logout('Sitzung abgelaufen. Bitte erneut anmelden.')
      } else {
        showMessage(error.message, 'error')
      }
    } finally {
      setBusy(false)
    }
  }

  function showMessage(text, type = '') {
    setMessage({ text, type })
  }

  function formatHeadline(nextGame) {
    if (!nextGame) {
      return 'Kein aktives Spiel.'
    }
    if (nextGame.status === 'won') {
      return `Spiel beendet: Spieler ${nextGame.winner} gewinnt.`
    }
    if (nextGame.status === 'draw') {
      return 'Spiel beendet: Unentschieden.'
    }
    return `Aktiver Zug: ${nextGame.current_player}`
  }

  function updateSession(nextData) {
    setSession((current) => ({ ...current, ...nextData }))
  }

  function onInputChange(event) {
    const { name, value } = event.target
    setCredentials((current) => ({ ...current, [name]: value }))
  }

  async function register(event) {
    event.preventDefault()
    setBusy(true)
    try {
      const payload = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(credentials),
      })
      updateSession({
        token: payload.access_token,
        userName: payload.user_name,
        userId: payload.user_id,
        gameId: null,
      })
      showMessage('Registrierung erfolgreich.', 'success')
    } catch (error) {
      showMessage(error.message, 'error')
    } finally {
      setBusy(false)
    }
  }

  async function login(event) {
    event.preventDefault()
    setBusy(true)
    try {
      const payload = await apiRequest('/auth/token', {
        method: 'POST',
        body: JSON.stringify({
          user_name: credentials.user_name,
          password: credentials.password,
        }),
      })
      updateSession({
        token: payload.access_token,
        userName: payload.user_name,
        userId: payload.user_id,
        gameId: null,
      })
      showMessage('Login erfolgreich.', 'success')
    } catch (error) {
      showMessage(error.message, 'error')
    } finally {
      setBusy(false)
    }
  }

  function logout(info = 'Abgemeldet.') {
    setSession({ token: '', userName: '-', userId: '', gameId: null })
    setGames([])
    setGame(null)
    setStatusText('Melde dich an oder registriere dich, um zu starten.')
    showMessage(info, '')
  }

  async function createGame() {
    setBusy(true)
    try {
      const newGame = await apiRequest('/games', { method: 'POST', headers: authHeaders })
      setGame(newGame)
      updateSession({ gameId: newGame.id })
      const allGames = await apiRequest('/games', { headers: authHeaders })
      setGames(allGames)
      setStatusText(formatHeadline(newGame))
      showMessage(`Neues Spiel #${newGame.id} erstellt.`, 'success')
    } catch (error) {
      showMessage(error.message, 'error')
    } finally {
      setBusy(false)
    }
  }

  async function loadGame(gameId) {
    setBusy(true)
    try {
      const loadedGame = await apiRequest(`/games/${gameId}`, { headers: authHeaders })
      setGame(loadedGame)
      updateSession({ gameId })
      setStatusText(formatHeadline(loadedGame))
      showMessage(`Spiel #${gameId} geladen.`, '')
    } catch (error) {
      showMessage(error.message, 'error')
    } finally {
      setBusy(false)
    }
  }

  async function playMove(position) {
    if (!game || !isOngoing) {
      return
    }
    setBusy(true)
    try {
      const movedGame = await apiRequest(`/games/${game.id}/move/${position}`, {
        method: 'PUT',
        headers: authHeaders,
      })
      setGame(movedGame)
      setStatusText(formatHeadline(movedGame))
      const allGames = await apiRequest('/games', { headers: authHeaders })
      setGames(allGames)
      showMessage('Zug gespeichert.', 'success')
    } catch (error) {
      showMessage(error.message, 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="hero-kicker">INSY Unterricht</p>
        <h1>TicTacToe Arena</h1>
        <p className="hero-text">React UI fuer Registrierung, Login, Spielzug und Historie auf eurer FastAPI.</p>
      </header>

      <section className="layout-grid">
        <article className="panel auth-panel">
          <h2>Account</h2>
          <form className="auth-form" onSubmit={register}>
            <label>
              Benutzername
              <input
                type="text"
                name="user_name"
                value={credentials.user_name}
                onChange={onInputChange}
                required
                minLength={3}
              />
            </label>
            <label>
              Passwort
              <input
                type="password"
                name="password"
                value={credentials.password}
                onChange={onInputChange}
                required
                minLength={6}
              />
            </label>
            <label>
              Anzeigename
              <input
                type="text"
                name="name"
                value={credentials.name}
                onChange={onInputChange}
                required
                minLength={2}
              />
            </label>
            <div className="button-row">
              <button type="submit" disabled={busy}>
                Registrieren
              </button>
              <button type="button" onClick={login} disabled={busy}>
                Login
              </button>
            </div>
          </form>
          <div className="session-card">
            <p>Benutzer: {session.userName || '-'}</p>
            <p>Token: {session.token ? 'gesetzt' : 'nicht gesetzt'}</p>
            <button type="button" className="ghost" onClick={() => logout()} disabled={busy}>
              Logout
            </button>
          </div>
        </article>

        <article className="panel board-panel">
          <div className="board-header">
            <h2>Spielfeld</h2>
            <button type="button" onClick={createGame} disabled={!session.token || busy}>
              Neues Spiel
            </button>
          </div>
          <p className="status-text">{statusText}</p>
          <div className="board">
            {board.map((cell, index) => (
              <button
                key={index}
                type="button"
                className="cell"
                onClick={() => playMove(index + 1)}
                disabled={busy || !isOngoing || Boolean(cell)}
              >
                {cell ?? ''}
              </button>
            ))}
          </div>
          {game ? <p className="meta-line">Aktives Spiel: #{game.id}</p> : null}
        </article>

        <article className="panel history-panel">
          <h2>Spielhistorie</h2>
          <ul className="history-list">
            {games.length === 0 ? <li>Keine Spiele vorhanden.</li> : null}
            {games.map((entry) => (
              <li key={entry.id}>
                <button
                  type="button"
                  className="history-button"
                  onClick={() => loadGame(entry.id)}
                  disabled={busy}
                >
                  <span>#{entry.id}</span>
                  <span>{entry.status}</span>
                  <span>{entry.winner ? `Gewinner ${entry.winner}` : '-'}</span>
                </button>
              </li>
            ))}
          </ul>
          <p className={`message ${message.type}`}>{message.text}</p>
        </article>
      </section>
    </main>
  )
}

export default App
