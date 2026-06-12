function PolicyPanel({ policy }) {
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

  const passages = parsePolicy(policy)

  return (
    <div className="sidebar">
      <div className="policy-header">📋 Policy [P1-P8]</div>
      {passages.map(p => (
        <div key={p.id} className="policy-item">
          <div className="policy-item-title">{p.id}</div>
          <div className="policy-item-content">{p.content.substring(0, 200)}...</div>
        </div>
      ))}
    </div>
  )
}

export default PolicyPanel