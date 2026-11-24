import { Chip, TextField, Autocomplete } from '@mui/material';

const [traditionConcepts, setTraditionConcepts] = useState<string[]>(category?.tradition_concepts || []);
const [philosophers, setPhilosophers] = useState<string[]>(category?.philosophers || []);

// В форме добавить:
<FormControl fullWidth margin="normal">
  <FormLabel>Traditions/Concepts (optional)</FormLabel>
  <Autocomplete
    multiple
    freeSolo
    options={[]} // Можно добавить предзаданные опции
    value={traditionConcepts}
    onChange={(event, newValue) => {
      setTraditionConcepts(newValue);
    }}
    renderTags={(value, getTagProps) =>
      value.map((option, index) => (
        <Chip
          label={option}
          {...getTagProps({ index })}
          variant="outlined"
        />
      ))
    }
    renderInput={(params) => (
      <TextField
        {...params}
        variant="outlined"
        placeholder="Enter traditions or concepts"
      />
    )}
  />
</FormControl>

<FormControl fullWidth margin="normal">
  <FormLabel>Philosophers (optional)</FormLabel>
  <Autocomplete
    multiple
    freeSolo
    options={[]} // Можно добавить предзаданные опции
    value={philosophers}
    onChange={(event, newValue) => {
      setPhilosophers(newValue);
    }}
    renderTags={(value, getTagProps) =>
      value.map((option, index) => (
        <Chip
          label={option}
          {...getTagProps({ index })}
          variant="outlined"
        />
      ))
    }
    renderInput={(params) => (
      <TextField
        {...params}
        variant="outlined"
        placeholder="Enter philosophers"
      />
    )}
  />
</FormControl>

// В onSubmit:
onSubmit({
  concept_id: conceptId,
  name,
  definition,
  extended_description: extendedDescription || undefined,
  source: source || undefined,
  tradition_concepts: traditionConcepts,
  philosophers: philosophers
});