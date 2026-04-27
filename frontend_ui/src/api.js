const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const SESSION_KEY = 'ttt_react_session'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  const payload = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new ApiError(payload.detail || `Request failed (${response.status})`, response.status)
  }

  return payload
}

export function readSession() {
  const raw = window.localStorage.getItem(SESSION_KEY)
  if (!raw) {
    return { token: '', userName: '-', userId: '', gameId: null }
  }

  try {
    const parsed = JSON.parse(raw)
    return {
      token: parsed.token || '',
      userName: parsed.userName || '-',
      userId: parsed.userId || '',
      gameId: parsed.gameId || null,
    }
  } catch {
    return { token: '', userName: '-', userId: '', gameId: null }
  }
}

export function saveSession(session) {
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function clearSession() {
  window.localStorage.removeItem(SESSION_KEY)
}
