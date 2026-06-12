import { useState } from 'react'

function StageInspector({ result }) {
  const [expanded, setExpanded] = useState({})

  const toggleStage = (n) => {
    setExpanded(prev => ({ ...prev, [n]: !prev[n] }))
  }

  const stages = [
    { n: 1, title: 'Stage 1: Classify', data: result.stage1_classification },
    { n: 2, title: 'Stage 2: Extract', data: result.stage2_extraction },
    { n: 3, title: 'Stage 3: Ground', data: result.stage3_grounded },
    { n: 4, title: 'Stage 4: Critique', data: result.stage4_critique },
  ]

  return (
    <div className="inspector">
      {stages.map(stage => (
        <div key={stage.n} className="stage">
          <div className="stage-header" onClick={() => toggleStage(stage.n)}>
            <span>{expanded[stage.n] ? '▼' : '▶'} {stage.title}</span>
          </div>
          {expanded[stage.n] && stage.data && (
            <div className="stage-content">
              {JSON.stringify(stage.data, null, 2)}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default StageInspector