// Обработка пикселей
for (let y = 0; y < height; y++) {
    // ... существующий код ...
    
    for (let x = 0; x < width; x++) {
        // ... конвертация координат в комплексное число ...
        const z = math.complex(re, im);
        
        // ВСТАВИТЬ КОД ОБРАБОТКИ ФАЗ ЗДЕСЬ
        // Применяем фазу аргумента, если она задана
        let zWithPhase;
        if (argumentPhase) {
            const r = math.abs(z);
            let theta = math.arg(z);
            theta += argumentPhase;
            zWithPhase = math.complex({
                r: r,
                phi: theta
            });
        } else {
            zWithPhase = z;
        }

        // Вычисляем значение функции
        let w;
        try {
            w = complexFunction(zWithPhase); // Используем zWithPhase вместо z
            
            // Применяем фазу функции, если она задана
            if (functionPhase) {
                const r = math.abs(w);
                let theta = math.arg(w);
                theta += functionPhase;
                w = math.complex({
                    r: r,
                    phi: theta
                });
            }
        } catch (error) {
            // В случае ошибки используем NaN
            w = math.complex(NaN, NaN);
        }
        
        // ... продолжение существующего кода для обработки результата ...
    }
}