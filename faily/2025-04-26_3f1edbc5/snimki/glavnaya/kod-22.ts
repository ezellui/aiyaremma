// В отображении информации о категории:
{selectedNode.tradition_concepts && selectedNode.tradition_concepts.length > 0 && (
  <div>
    <strong>Traditions/Concepts:</strong>
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '5px' }}>
      {selectedNode.tradition_concepts.map((tradition, index) => (
        <Chip key={index} label={tradition} size="small" />
      ))}
    </div>
  </div>
)}
{selectedNode.philosophers && selectedNode.philosophers.length > 0 && (
  <div style={{ marginTop: '10px' }}>
    <strong>Philosophers:</strong>
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '5px' }}>
      {selectedNode.philosophers.map((philosopher, index) => (
        <Chip key={index} label={philosopher} size="small" />
      ))}
    </div>
  </div>
)}

// В отображении информации о связи:
{selectedEdge.tradition_concepts && selectedEdge.tradition_concepts.length > 0 && (
  <div>
    <strong>Traditions/Concepts:</strong>
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '5px' }}>
      {selectedEdge.tradition_concepts.map((tradition, index) => (
        <Chip key={index} label={tradition} size="small" />
      ))}
    </div>
  </div>
)}
{selectedEdge.philosophers && selectedEdge.philosophers.length > 0 && (
  <div style={{ marginTop: '10px' }}>
    <strong>Philosophers:</strong>
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginTop: '5px' }}>
      {selectedEdge.philosophers.map((philosopher, index) => (
        <Chip key={index} label={philosopher} size="small" />
      ))}
    </div>
  </div>
)}