if (linkClickCount === 2) {
    // Двойной клик - просмотр связи
    const connectionData = {
        source: d.source,
        target: d.target,
        type: d.type,
        weight: d.weight,
        bidirectional: d.bidirectional,
        description: d.description
    };
    openUniversalModal('connection', connectionData, 'view');
}