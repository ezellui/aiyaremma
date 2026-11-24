// Message handler
self.onmessage = function(e) {
    if (e.data.type === 'calculate') {
        try {
            const result = domainColoring(e.data.params);
            self.postMessage({
                type: 'result',
                imageData: result.imageData,
                zeros: result.zeros,
                poles: result.poles
            }, [result.imageData.buffer]);
        } catch (error) {
            self.postMessage({
                type: 'error',
                message: error.message
            });
        }
    }
};