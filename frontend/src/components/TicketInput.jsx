import { useState } from 'react'

function TicketInput({ onSend, testTickets, disabled }) {
  const [ticketText, setTicketText] = useState('')
  const [selectedId, setSelectedId] = useState('')

  const handleSend = () => {
    onSend(ticketText, null)
    setTicketText('')
  }

  const handleTestTicket = (e) => {
    const id = parseInt(e.target.value)
    if (id) {
      const ticket = testTickets.find(t => t.id === id)
      if (ticket) {
        onSend(ticket.raw_ticket, id)
        setSelectedId('')
      }
    }
  }

  return (
    <div className="input-container">
      <select 
        className="ticket-selector"
        value={selectedId}
        onChange={handleTestTicket}
        disabled={disabled}
      >
        <option value="">📝 Or pick a test ticket...</option>
        {testTickets.map(ticket => (
          <option key={ticket.id} value={ticket.id}>
            {ticket.id} - {ticket.raw_ticket.substring(0, 50)}...
          </option>
        ))}
      </select>

      <textarea
        value={ticketText}
        onChange={(e) => setTicketText(e.target.value)}
        placeholder="Paste a support ticket here..."
        disabled={disabled}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && e.ctrlKey) {
            handleSend()
          }
        }}
      />

      <div className="button-group">
        <button 
          className="primary"
          onClick={handleSend}
          disabled={disabled || !ticketText.trim()}
        >
          Send Ticket (Ctrl+Enter)
        </button>
        <button 
          className="secondary"
          onClick={() => setTicketText('')}
          disabled={disabled}
        >
          Clear
        </button>
      </div>
    </div>
  )
}

export default TicketInput