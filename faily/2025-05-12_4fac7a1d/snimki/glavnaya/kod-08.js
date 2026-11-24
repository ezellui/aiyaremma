function initWorker() {
    const workerCode = `
        // Импорт math.js
        importScripts('https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.5.0/math.min.js');
        
        // Complex math functions
        const ComplexMath = {
            // ... существующие функции ...
        };
        
        // Process a summation expression
        function processSummation(expression) {
            // ... существующий код ...
        }
        
        // Process a differentiation expression
        function processDifferentiation(expression) {
            // ... существующий код ...
        }
        
        // Create a complex function evaluator
        function createComplexFunction(expression) {
            // ... существующий код ...
        }
        
        // Implementation of domain coloring algorithm
        function domainColoring(params) {
            const { expression, width, height, xMin, xMax, yMin, yMax, 
                    colorScheme, showGrid, gridDensity, showAxes,
                    applyDerivative, applyInverse } = params;
            
            // ... остальной существующий код domainColoring ...
        }
        
        // Функция для создания преобразованной решётки
        function createTransformedGrid(params) {
            const { 
                width, height, expression, xMin, xMax, yMin, yMax, 
                colorScheme, gridDensity, gridThickness, showAxes,
                applyDerivative, applyInverse, argumentPhase, functionPhase 
            } = params;
            
            // Создаём буфер для изображения
            const imageData = new Uint8ClampedArray(width * height * 4);
            
            // Создаём функцию комплексного переменного
            let complexFunction = createComplexFunction(expression);
            
            // Применяем преобразования
            if (applyDerivative) {
                const originalFunction = complexFunction;
                complexFunction = function(z) {
                    return ComplexMath.derivative(originalFunction, z);
                };
            }
            
            if (applyInverse) {
                const originalFunction = complexFunction;
                complexFunction = function(z) {
                    return originalFunction(math.divide(1, z));
                };
            }
            
            // Параметры отображения решётки
            const gridSpacing = 1 / (gridDensity || 0.5); // Расстояние между линиями
            
            // Размеры шага
            const scaleX = (xMax - xMin) / width;
            const scaleY = (yMax - yMin) / height;
            
            // Множитель для яркости линий решётки
            const gridBrightness = 1.3;
            
            // Масштаб для градиента линий
            const gradientScale = 0.5;
            
            // Сканируем по пикселям
            for (let y = 0; y < height; y++) {
                // Отображаем прогресс каждые 10% строк
                if (y % Math.floor(height / 10) === 0) {
                    const progress = Math.round((y / height) * 100);
                    self.postMessage({ type: 'progress', progress });
                }
                
                for (let x = 0; x < width; x++) {
                    // Преобразуем координаты холста в комплексную плоскость
                    const re = xMin + x * scaleX;
                    const im = yMax - y * scaleY;
                    const z = math.complex(re, im);
                    
                    // Применяем фазу аргумента
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
                        w = complexFunction(zWithPhase);
                        
                        // Применяем фазу функции
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
                    
                    // Индекс пикселя в буфере изображения
                    const pixelIndex = (y * width + x) * 4;
                    
                    // Проверяем на NaN и бесконечность
                    if (isNaN(math.re(w)) || isNaN(math.im(w)) || 
                        !isFinite(math.re(w)) || !isFinite(math.im(w))) {
                        // Устанавливаем цвет для undefined
                        imageData[pixelIndex] = 0;     // R
                        imageData[pixelIndex + 1] = 0; // G
                        imageData[pixelIndex + 2] = 0; // B
                        imageData[pixelIndex + 3] = 255; // A
                        continue;
                    }
                    
                    // Получаем действительную и мнимую части
                    const wReal = math.re(w);
                    const wImag = math.im(w);
                    
                    // Проверяем, находится ли точка вблизи линии преобразованной решётки
                    const realMod = Math.abs(wReal % gridSpacing);
                    const imagMod = Math.abs(wImag % gridSpacing);
                    
                    const isOnGridReal = Math.min(realMod, gridSpacing - realMod) < gridThickness;
                    const isOnGridImag = Math.min(imagMod, gridSpacing - imagMod) < gridThickness;
                    
                    // Получаем модуль и аргумент
                    const modulus = math.abs(w);
                    const phase = math.arg(w);
                    
                    // Нормализуем фазу в диапазон [0, 1]
                    const normalizedPhase = (phase + Math.PI) / (2 * Math.PI);
                    
                    // Вычисляем яркость на основе модуля
                    const brightness = 0.5 + 0.5 * Math.tanh(modulus - 1);
                    
                    // Определяем базовый цвет в зависимости от выбранной цветовой схемы
                    let r, g, b;
                    
                    switch (colorScheme) {
                        case 'standard':
                            // HSV to RGB с фазой как оттенком и модулем как яркостью
                            const hue = normalizedPhase * 360;
                            [r, g, b] = hsvToRgb(hue, 0.8, brightness);
                            break;
                            
                        case 'hsl':
                            // Прямое отображение HSL
                            [r, g, b] = hslToRgb(normalizedPhase, 1, 0.5);
                            break;
                            
                        case 'grayscale':
                            // Используем только яркость на основе модуля
                            r = g = b = Math.floor(brightness * 255);
                            break;
                            
                        case 'sunset':
                            // Цветовая схема в стиле заката
                            r = Math.floor(255 * (0.5 + 0.5 * Math.sin(normalizedPhase * Math.PI)));
                            g = Math.floor(150 * brightness);
                            b = Math.floor(100 * (1 - brightness) + 50);
                            break;
                            
                        case 'ocean':
                            // Цветовая схема в стиле океана
                            r = Math.floor(50 * brightness);
                            g = Math.floor(100 + 155 * normalizedPhase * brightness);
                            b = Math.floor(150 + 105 * brightness);
                            break;
                            
                        case 'phase':
                            // Чистое фазовое окрашивание
                            [r, g, b] = hslToRgb(normalizedPhase, 1, 0.5);
                            break;
                            
                        case 'modulus':
                            // Чистое окрашивание по модулю
                            const modulusColor = 0.5 + 0.5 * Math.tanh(modulus / 2);
                            r = g = b = Math.floor(modulusColor * 255);
                            break;
                            
                        default:
                            // По умолчанию: стандартная схема
                            const defaultHue = normalizedPhase * 360;
                            [r, g, b] = hsvToRgb(defaultHue, 0.8, brightness);
                    }
                    
                    // Применяем преобразованные линии решётки
                    if (isOnGridReal || isOnGridImag) {
                        // Создаём градиент для линий решётки с плавными переходами
                        // Вычисляем "глубину" внутри линии (0 в центре, 1 на краю)
                        let lineDepth = 1.0;
                        
                        if (isOnGridReal) {
                            const depthReal = Math.min(realMod, gridSpacing - realMod) / gridThickness;
                            lineDepth = Math.min(lineDepth, depthReal);
                        }
                        
                        if (isOnGridImag) {
                            const depthImag = Math.min(imagMod, gridSpacing - imagMod) / gridThickness;
                            lineDepth = Math.min(lineDepth, depthImag);
                        }
                        
                        // Создаём плавный градиент на основе расстояния от центра линии
                        const gradientFactor = Math.pow(lineDepth, 0.5);
                        
                        // Делаем линии ярче, учитывая градиент
                        r = Math.min(255, Math.floor(r * (1 + (gridBrightness - 1) * (1 - gradientFactor))));
                        g = Math.min(255, Math.floor(g * (1 + (gridBrightness - 1) * (1 - gradientFactor))));
                        b = Math.min(255, Math.floor(b * (1 + (gridBrightness - 1) * (1 - gradientFactor))));
                        
                        // Добавляем цветовые акценты в зависимости от положения в комплексной плоскости
                        // Создаем переливающийся эффект на основе фазы и модуля
                        const waveEffect = Math.sin(wReal * gradientScale) * Math.cos(wImag * gradientScale);
                        const colorShift = 30 * (1 - gradientFactor) * waveEffect;
                        
                        if (waveEffect > 0) {
                            r = Math.min(255, r + colorShift);
                            b = Math.max(0, b - colorShift);
                        } else {
                            b = Math.min(255, b - colorShift);
                            g = Math.max(0, g + colorShift);
                        }
                    }
                    
                    // Добавляем оси при необходимости
                    if (showAxes) {
                        const axisWidth = 0.1;
                        
                        // Действительная ось (Im(w) = 0)
                        if (Math.abs(wImag) < axisWidth) {
                            r = Math.min(255, r + 50);
                            g = Math.min(255, g + 50);
                            b = Math.min(255, b + 50);
                        }
                        
                        // Мнимая ось (Re(w) = 0)
                        if (Math.abs(wReal) < axisWidth) {
                            r = Math.min(255, r + 50);
                            g = Math.min(255, g + 50);
                            b = Math.min(255, b + 50);
                        }
                    }
                    
                    // Устанавливаем цвет пикселя
                    imageData[pixelIndex] = r;
                    imageData[pixelIndex + 1] = g;
                    imageData[pixelIndex + 2] = b;
                    imageData[pixelIndex + 3] = 255;
                }
            }
            
            // Возвращаем созданное изображение
            return { imageData };
        }
        
        // Helper function: HSV to RGB conversion
        function hsvToRgb(h, s, v) {
            let r, g, b;
            
            const i = Math.floor(h / 60) % 6;
            const f = h / 60 - i;
            const p = v * (1 - s);
            const q = v * (1 - f * s);
            const t = v * (1 - (1 - f) * s);
            
            switch (i) {
                case 0: r = v; g = t; b = p; break;
                case 1: r = q; g = v; b = p; break;
                case 2: r = p; g = v; b = t; break;
                case 3: r = p; g = q; b = v; break;
                case 4: r = t; g = p; b = v; break;
                case 5: r = v; g = p; b = q; break;
            }
            
            return [Math.floor(r * 255), Math.floor(g * 255), Math.floor(b * 255)];
        }
        
        // Helper function: HSL to RGB conversion
        function hslToRgb(h, s, l) {
            let r, g, b;
            
            if (s === 0) {
                r = g = b = l; // achromatic
            } else {
                const hue2rgb = (p, q, t) => {
                    if (t < 0) t += 1;
                    if (t > 1) t -= 1;
                    if (t < 1/6) return p + (q - p) * 6 * t;
                    if (t < 1/2) return q;
                    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                    return p;
                };
                
                const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
                const p = 2 * l - q;
                
                r = hue2rgb(p, q, h + 1/3);
                g = hue2rgb(p, q, h);
                b = hue2rgb(p, q, h - 1/3);
            }
            
            return [Math.floor(r * 255), Math.floor(g * 255), Math.floor(b * 255)];
        }
        
        // Message handler
        self.onmessage = function(e) {
            if (e.data.type === 'calculate') {
                try {
                    let result;
                    
                    // Выбираем метод визуализации в зависимости от параметра
                    if (e.data.params.useTransformedGrid) {
                        // Используем преобразованную решётку
                        result = createTransformedGrid(e.data.params);
                    } else {
                        // Используем стандартный алгоритм
                        result = domainColoring(e.data.params);
                    }
                    
                    self.postMessage({
                        type: 'result',
                        imageData: result.imageData,
                        zeros: result.zeros || [],
                        poles: result.poles || []
                    }, [result.imageData.buffer]);
                } catch (error) {
                    self.postMessage({
                        type: 'error',
                        message: error.message
                    });
                }
            }
        };
    `;
    
    const blob = new Blob([workerCode], { type: 'application/javascript' });
    worker = new Worker(URL.createObjectURL(blob));
    
    // ...остальной код обработчиков...
}