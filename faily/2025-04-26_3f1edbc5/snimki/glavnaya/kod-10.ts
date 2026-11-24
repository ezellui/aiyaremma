const [traditionConcept, setTraditionConcept] = useState(connection?.tradition_concept || '');
const [philosopher, setPhilosopher] = useState(connection?.philosopher || '');

// В форме добавить:
<FormControl fullWidth margin="normal">
  <FormLabel>Tradition/Concept (optional)</FormLabel>
  <TextField
    value={traditionConcept}
    onChange={(e) => setTraditionConcept(e.target.value)}
    placeholder="Enter tradition or concept"
    fullWidth
    variant="outlined"
  />
</FormControl>

<FormControl fullWidth margin="normal">
  <FormLabel>Philosopher (optional)</FormLabel>
  <TextField
    value={philosopher}
    onChange={(e) => setPhilosopher(e.target.value)}
    placeholder="Enter philosopher"
    fullWidth
    variant="outlined"
  />
</FormControl>

// В onSubmit добавить:
onSubmit({
  concept_id: conceptId,
  source_category_id: sourceId,
  target_category_id: targetId,
  connection_type: connectionType as any,
  direction: direction as any,
  description: description || undefined,
  tradition_concept: traditionConcept || undefined,  // Добавлено
  philosopher: philosopher || undefined             // Добавлено
});