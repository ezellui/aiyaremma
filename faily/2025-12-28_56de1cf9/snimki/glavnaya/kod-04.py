def analyze_amplitude_solutions(mu0, g, D, L):
    """Анализирует различные решения амплитудного уравнения"""
    X = np.linspace(0, L, 1000)
    
    # 1. Однородное решение
    A_uniform = np.sqrt(mu0/g) * np.ones_like(X)
    
    # 2. Локализованная структура
    X0 = L/2
    width = np.sqrt(D/mu0)
    A_localized = np.sqrt(mu0/g) * (1/np.cosh((X - X0)/width))
    
    # 3. Фронт
    A_front = np.sqrt(mu0/g) * np.tanh((X - L/2)/width)
    
    # 4. Периодическая модуляция
    k_mod = np.pi/L
    A_modulated = np.sqrt(mu0/g) * (1 + 0.3*np.cos(k_mod*X))
    
    # Визуализация
    plt.figure(figsize=(12, 8))
    
    solutions = [
        ('Однородный', A_uniform),
        ('Локализованный', A_localized),
        ('Фронт', A_front),
        ('Модулированный', A_modulated)
    ]
    
    for i, (name, A) in enumerate(solutions):
        plt.subplot(2, 2, i+1)
        plt.plot(X, A, 'b-', linewidth=2)
        plt.xlabel('X')
        plt.ylabel('A(X)')
        plt.title(name)
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('amplitude_solutions.png', dpi=150)
    
    return solutions