def analyze_resonance(period_range, fixed_alpha=1.0):
    """Анализирует резонансные эффекты при разных периодах"""
    
    amplitudes = []
    periods = []
    
    for period in period_range:
        print(f"Период: {period:.2f}")
        
        model = PowerSocietyModelPeriodic(
            Nx=200,
            eps1_sq=0.005,
            eps2_sq=0.2,
            alpha_parameter=fixed_alpha,
            period=period,
            amplitude=0.2
        )
        
        # Начальное условие
        p0 = 0.3 + 0.4 * (1 + np.tanh((model.x - 0.5) / 0.05))
        s0 = 0.5 * np.ones(model.Nx)
        
        # Симуляция (несколько периодов)
        T = 5 * period
        dt = 0.05
        times, p_hist, s_hist, r_hist = model.simulate_periodic(p0, s0, T, dt)
        
        # Амплитуда колебаний r(t) на последнем периоде
        last_period_start = int(4 * period / dt)
        r_last_period = r_hist[last_period_start:]
        amplitude = (r_last_period.max() - r_last_period.min()) / 2
        
        amplitudes.append(amplitude)
        periods.append(period)
    
    # Визуализация резонансной кривой
    plt.figure(figsize=(10, 6))
    plt.plot(periods, amplitudes, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('Период внешнего воздействия T')
    plt.ylabel('Амплитуда колебаний Δr')
    plt.title(f'Резонансная кривая (α = {fixed_alpha})')
    plt.grid(True)
    plt.savefig('resonance_curve.png', dpi=150)
    plt.show()
    
    # Найти резонансные пики
    peaks = []
    for i in range(1, len(amplitudes)-1):
        if amplitudes[i] > amplitudes[i-1] and amplitudes[i] > amplitudes[i+1]:
            peaks.append((periods[i], amplitudes[i]))
    
    print("\nРезонансные пики:")
    for T, A in peaks:
        print(f"  T = {T:.2f}, Амплитуда = {A:.4f}")
    
    return periods, amplitudes, peaks

# Запуск анализа
period_range = np.linspace(5, 50, 20)
analyze_resonance(period_range, fixed_alpha=1.0)