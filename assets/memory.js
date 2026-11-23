'use strict';

const search = document.getElementById('memory-query');
const group = document.getElementById('memory-group');
const count = document.getElementById('memory-result-count');
const rows = [...document.querySelectorAll('[data-memory]')];
const normalize = value => value.toLocaleLowerCase('ru').replace(/ё/g,'е');

function filterMemory() {
  const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
  const selected = group.value;
  let shown = 0;
  for (const row of rows) {
    const text = window.memorySearch[row.dataset.memory];
    const matches = (!selected || selected === row.dataset.category)
      && terms.every(term => text.includes(term));
    row.hidden = !matches;
    if (matches) shown++;
  }
  count.textContent = shown ? 'Записей: ' + shown : 'Записи не найдены';
  for (const section of document.querySelectorAll('.memory-category')) {
    section.hidden = !section.querySelector('[data-memory]:not([hidden])');
  }
}
search.addEventListener('input',filterMemory);
group.addEventListener('change',filterMemory);
filterMemory();
