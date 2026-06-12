import { useState } from 'react'

function PolicyPanel({ policy }) {
  const [isOpen, setIsOpen] = useState(false)
  const [expandedPolicy, setExpandedPolicy] = useState({})

  // Parse policy passages [P1]-[P8]
  const parsePolicy = (text) => {
    const regex = /\[P(\d+)\](.*?)(?=\[P\d+\]|$)/gs
    const matches = []
    let match
    while ((match = regex.exec(text)) !== null) {
      matches.push({
        id: `P${match[1]}`,
        content: match[2].trim()
      })
    }
    return matches
  }

  const togglePolicy = (id) => {
    setExpandedPolicy(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const passages = parsePolicy(policy)

  return (
    <>
      {/* Floating Button */}
      <button 
        className="policy-button"
        onClick={() => setIsOpen(!isOpen)}
        title="View Policy"
      >
        📋
      </button>

      {/* Modal Dropdown */}
      {isOpen && (
        <div className="policy-modal">
          <div className="policy-modal-header">
            <span>📋 Support Policy [P1-P8]</span>
            <button 
              className="close-button"
              onClick={() => setIsOpen(false)}
            >
              ✕
            </button>
          </div>

          <div className="policy-modal-content">
            {passages.map(p => (
              <div key={p.id} className="policy-dropdown-item">
                <div 
                  className="policy-dropdown-header"
                  onClick={() => togglePolicy(p.id)}
                >
                  <span className="policy-id">{p.id}</span>
                  <span className="toggle-arrow">{expandedPolicy[p.id] ? '▼' : '▶'}</span>
                </div>

                {expandedPolicy[p.id] && (
                  <div className="policy-dropdown-text">
                    {p.content}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

export default PolicyPanel