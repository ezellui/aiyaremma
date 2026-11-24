// В отображении информации о категории добавить:
{selectedNode.tradition_concept && (
  <p><strong>Tradition/Concept:</strong> {selectedNode.tradition_concept}</p>
)}
{selectedNode.philosopher && (
  <p><strong>Philosopher:</strong> {selectedNode.philosopher}</p>
)}

// В отображении информации о связи добавить:
{selectedEdge.tradition_concept && (
  <p><strong>Tradition/Concept:</strong> {selectedEdge.tradition_concept}</p>
)}
{selectedEdge.philosopher && (
  <p><strong>Philosopher:</strong> {selectedEdge.philosopher}</p>
)}