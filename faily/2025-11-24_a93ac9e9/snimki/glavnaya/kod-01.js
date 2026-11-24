function updateGraphData() {
    // Пересоздаем links из connections
    links = connections.map(conn => ({
        source: conn.from,    // ← Преобразование from -> source
        target: conn.to,      // ← Преобразование to -> target
        type: conn.type,
        weight: conn.weight || 2,
        bidirectional: conn.bidirectional || false
    }));
}