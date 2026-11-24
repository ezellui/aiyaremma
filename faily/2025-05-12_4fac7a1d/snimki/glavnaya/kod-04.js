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