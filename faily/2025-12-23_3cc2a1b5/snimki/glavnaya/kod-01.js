// Добавить философа
{ 
    id: "anselm", name: "Ансельм Кентерберийский"
}

// Концепции Ансельма
{ 
    id: "ontological_argument", 
    label: "Онтологический аргумент", 
    philosopher: "anselm"
},
{ 
    id: "faith_seeking_understanding", 
    label: "Fides quaerens intellectum", 
    philosopher: "anselm"
},
{ 
    id: "id_quo_maius", 
    label: "То, больше чего нельзя помыслить", 
    philosopher: "anselm"
},
{ 
    id: "necessary_existence", 
    label: "Необходимое существование", 
    philosopher: "anselm"
},
{ 
    id: "truth_as_rectitudo", 
    label: "Истина как правильность", 
    philosopher: "anselm"
},
{ 
    id: "cur_deus_homo", 
    label: "Cur Deus Homo", 
    philosopher: "anselm"
}

// Связи между концепциями Ансельма и других философов

// ПЛАТОН → АНСЕЛЬМ
{ source: "ideas", target: "id_quo_maius", type: "influence", weight: 2 },
{ source: "eidos", target: "truth_as_rectitudo", type: "influence", weight: 1 },

// АВГУСТИН → АНСЕЛЬМ
{ source: "faith_reason", target: "faith_seeking_understanding", type: "develop", weight: 3 },
{ source: "grace", target: "cur_deus_homo", type: "influence", weight: 2 },
{ source: "original_sin", target: "cur_deus_homo", type: "presuppose", weight: 2 },

// АНСЕЛЬМ → ФОМА АКВИНСКИЙ
{ source: "ontological_argument", target: "five_ways", type: "oppose", weight: 3, bidirectional: true },
{ source: "necessary_existence", target: "essence_existence", type: "influence", weight: 2 },

// АНСЕЛЬМ → ДУНС СКОТ
{ source: "necessary_existence", target: "infinity_scotus", type: "develop", weight: 2 },
{ source: "ontological_argument", target: "formal_distinction", type: "develop", weight: 2 },

// АНСЕЛЬМ → ДЕКАРТ
{ source: "ontological_argument", target: "infinite_idea", type: "develop", weight: 3 },
{ source: "id_quo_maius", target: "clear_distinct", type: "influence", weight: 2 },

// АНСЕЛЬМ → СПИНОЗА
{ source: "necessary_existence", target: "substance_spinoza", type: "develop", weight: 2 },
{ source: "ontological_argument", target: "deus_sive_natura", type: "influence", weight: 2 },

// АНСЕЛЬМ → ЛЕЙБНИЦ
{ source: "ontological_argument", target: "possible_worlds", type: "develop", weight: 2 },
{ source: "necessary_existence", target: "sufficient_reason", type: "influence", weight: 2 },
{ source: "ontological_argument", target: "theodicy", type: "influence", weight: 1 },

// АНСЕЛЬМ → КАНТ
{ source: "ontological_argument", target: "thing_itself", type: "critique", weight: 3, bidirectional: true },
{ source: "ontological_argument", target: "synthetic_apriori", type: "critique", weight: 2, bidirectional: true },

// АНСЕЛЬМ → ГЕГЕЛЬ
{ source: "ontological_argument", target: "dialectic", type: "dialogue", weight: 2 },
{ source: "id_quo_maius", target: "absolute_idea", type: "influence", weight: 2 }