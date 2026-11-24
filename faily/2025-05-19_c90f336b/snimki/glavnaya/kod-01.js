// Добавить в объект Complex в Web Worker
floor: function(a) {
    return {
        re: Math.floor(a.re),
        im: Math.floor(a.im)
    };
},
ceil: function(a) {
    return {
        re: Math.ceil(a.re),
        im: Math.ceil(a.im)
    };
},
conj: function(a) {
    return {
        re: a.re,
        im: -a.im
    };
},