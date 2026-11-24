// Внутренние связи АНСЕЛЬМ - АНСЕЛЬМ

// Методологическая основа для аргумента
{ source: "faith_seeking_understanding", target: "ontological_argument", type: "instrument", weight: 3 },

// Определение Бога как условие аргумента
{ source: "id_quo_maius", target: "ontological_argument", type: "presuppose", weight: 3 },

// Аргумент выводит необходимое существование
{ source: "ontological_argument", target: "necessary_existence", type: "consequence", weight: 3 },

// Необходимое существование и совершенство связаны
{ source: "necessary_existence", target: "id_quo_maius", type: "complement", weight: 2, bidirectional: true },

// Методологический принцип применяется к теории искупления
{ source: "faith_seeking_understanding", target: "cur_deus_homo", type: "instrument", weight: 3 },

// Теория искупления предполагает необходимое существование Бога
{ source: "cur_deus_homo", target: "necessary_existence", type: "presuppose", weight: 2 },

// Концепция истины связана с методологией
{ source: "truth_as_rectitudo", target: "faith_seeking_understanding", type: "complement", weight: 2 },

// Истина как правильность применяется к теории искупления
{ source: "truth_as_rectitudo", target: "cur_deus_homo", type: "apply", weight: 2 },

// Онтологический аргумент и теория истины в диалоге
{ source: "ontological_argument", target: "truth_as_rectitudo", type: "dialogue", weight: 1, bidirectional: true }