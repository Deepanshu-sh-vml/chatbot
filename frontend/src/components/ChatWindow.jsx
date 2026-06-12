import { forwardRef } from 'react'

const ChatWindow = forwardRef(({ messages, loading }, ref) => {
  return (
    <div className="chat-window">
      {messages.length === 0 && !loading && (
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%',
          color: '#999',
          textAlign: 'center',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <div style={{ fontSize: '48px' }}>💬</div>
          <div>
            <p>Welcome to Northwind Support Co-pilot!</p>
            <p style={{ fontSize: '12px', marginTop: '8px' }}>Paste a support ticket or select a test case to get started.</p>
          </div>
        </div>
      )}

      {messages.map(msg => (
        <div key={msg.id} className={`message ${msg.role}`}>
          <div className="message-bubble">
            {msg.isManual ? (
              <>
                <div style={{ marginBottom: '12px' }}>{msg.text}</div>
                <div className="manual-prompt">
                  <div className="manual-prompt-header">📋 Assembled Prompt (copy & paste into ChatGPT):</div>
                  <div className="prompt-text">{msg.assembled_prompt}</div>
                  <button 
                    className="copy-button"
                    onClick={() => navigator.clipboard.writeText(msg.assembled_prompt)}
                  >
                    📋 Copy Prompt
                  </button>
                </div>
              </>
            ) : msg.isError ? (
              <span style={{ color: '#ef4444' }}>{msg.text}</span>
            ) : (
              <>
                {msg.text}
                {msg.stage3 && (
                  <div style={{ marginTop: '12px', fontSize: '12px', opacity: 0.8 }}>
                    <div className={`behavior-badge ${msg.stage3.behavior}`}>
                      {msg.stage3.behavior.replace(/_/g, ' ').toUpperCase()}
                    </div>
                    {msg.stage3.citations.length > 0 && (
                      <div style={{ marginTop: '8px' }}>
                        <strong>Citations:</strong> {msg.stage3.citations.join(', ')}
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      ))}

      {loading && (
        <div className="message bot">
          <div className="message-bubble">
            <div className="loading">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}

      <div ref={ref} />
    </div>
  )
})

ChatWindow.displayName = 'ChatWindow'

export default ChatWindow