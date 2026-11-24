const [traditionConcept, setTraditionConcept] = useState(category?.tradition_concept || '');
const [philosopher, setPhilosopher] = useState(category?.philosopher || '');

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
  name,
  definition,
  extended_description: extendedDescription || undefined,
  source: source || undefined,
  tradition_concept: traditionConcept || undefined,  // Добавлено
  philosopher: philosopher || undefined             // Добавлено
});