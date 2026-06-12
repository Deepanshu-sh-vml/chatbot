import { useEffect, useState, useRef } from 'react'
import ChatWindow from './components/ChatWindow'
import TicketInput from './components/TicketInput'
import StageInspector from './components/StageInspector'
import PolicyPanel from './components/PolicyPanel'
import * as api from './api'

function App() {
  const [health, setHealth] = useState(null)
  const [tickets, setTickets] = useState([])
  const [policy, setPolicy] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [showInspector, setShowInspector] = useState(false)
  const [lastResult, setLastResult] = useState(null)
  const [error, setError] = useState(null)
  const chatEndRef = useRef(null)

  // Fetch initial data
  useEffect(() => {
    const init = async () => {
      try {
        const h = await api.getHealth()
        setHealth(h)
        
        const t = await api.getTickets()
        setTickets(t)
        
        const p = await api.getPolicy()
        setPolicy(p)
      } catch (err) {
        setError('Failed to connect to backend. Make sure it\'s running on http://localhost:8000')
      }
    }
    init()
  }, [])

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendTicket = async (ticketText, ticketId = null) => {
    if (!ticketText.trim()) return

    setError(null)
    setLoading(true)
    setShowInspector(false)

    try {
      // Add user message
      setMessages(prev => [...prev, { 
        role: 'user', 
        text: ticketText,
        id: Date.now()
      }])

      let result
      if (ticketId) {
        result = await api.runTicketById(ticketId)
      } else {
        result = await api.sendTicket(ticketText)
      }

      setLastResult(result)

      // Check for manual mode
      if (result.mode === 'manual') {
        setMessages(prev => [...prev, {
          role: 'bot',
          text: result.message,
          assembled_prompt: result.assembled_prompt,
          isManual: true,
          id: Date.now()
        }])
      } else {
        // Add bot response
        setMessages(prev => [...prev, {
          role: 'bot',
          text: result.final_reply,
          stage3: result.stage3_grounded,
          id: Date.now()
        }])
      }
    } catch (err) {
      setError(err.message)
      setMessages(prev => [...prev, {
        role: 'bot',
        text: `Error: ${err.message}`,
        isError: true,
        id: Date.now()
      }])
    } finally {
      setLoading(false)
    }
  }

  const statusMode = health?.mode || 'unknown'
  const statusOk = health?.status === 'ok'

  return (
    <div className="app-container">
      <div className="main-content">
        <div className="header">
          <h1>🎯 Northwind Support Co-pilot</h1>
          {/* <div className="status">
            <span className={`status-dot ${statusOk ? (statusMode === 'manual' ? 'manual' : 'ok') : 'error'}`}></span>
            <span>{statusOk ? (statusMode === 'manual' ? 'Manual Mode (no API key)' : 'Connected') : 'Offline'}</span>
          </div> */}
        </div>

        {error && <div className="error-box">{error}</div>}

        <ChatWindow 
          messages={messages} 
          loading={loading}
          ref={chatEndRef}
        />

        <div className="input-area">
          <TicketInput 
            onSend={handleSendTicket}
            testTickets={tickets}
            disabled={loading || !statusOk}
          />

          {lastResult && !error && (
            <>
              <div className="inspector-toggle" onClick={() => setShowInspector(!showInspector)}>
                <span>{showInspector ? '▼' : '▶'}</span>
                <span>Show Pipeline Details</span>
              </div>
              {showInspector && <StageInspector result={lastResult} />}
            </>
          )}
        </div>
      </div>

      {policy && <PolicyPanel policy={policy.passages} />}
    </div>
  )
}

export default App