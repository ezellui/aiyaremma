class PowerSocietyModelPeriodic(PowerSocietyModel):
    """Модель с периодическим изменением настроений общества"""
    
    def __init__(self, *args, alpha_parameter=0.5, period=10.0, amplitude=0.3, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha_param = alpha_parameter  # параметр α из статьи
        self.period = period
        self.amplitude = amplitude
        self.omega = 2 * np.pi / period
        
    def phi2(self, x, t):
        """Периодическая функция φ₂(x,t) = φ₂⁽⁰⁾(x) + A(x)sin(ωt)"""
        phi2_0 = 0.5 - 0.3*x  # базовое распределение
        modulation = self.amplitude * np.sin(self.omega * t**self.alpha_param)
        return phi2_0 + modulation * (1 - x)  # амплитуда зависит от уровня
    
    def reaction_p_periodic(self, p, s, t):
        """Реакционный член с учётом φ₂(x,t)"""
        phi1 = 0.2 * np.ones_like(self.x)
        phi2 = self.phi2(self.x, t)
        phi3 = 0.8 * np.ones_like(self.x)
        
        # Исходная модель Петрова: -k(p-φ₁)(p-φ₂)(p-φ₃)
        k = 1.0
        reaction_original = -k * (p - phi1) * (p - phi2) * (p - phi3)
        
        # Взаимодействие с обществом
        reaction_society = -self.alpha * p * s
        
        return reaction_original + reaction_society
    
    def step_implicit_periodic(self, p, s, t, dt):
        """Полунеявный шаг с периодическим воздействием"""
        Nx = self.Nx
        I = diags([1.0]*Nx, 0, format='csr')
        
        # Для p (с учётом периодического члена)
        A_p = I - dt * self.eps1_sq * self.laplacian
        b_p = p + dt * self.reaction_p_periodic(p, s, t)
        p_new = spsolve(A_p, b_p)
        
        # Для s (без изменений)
        A_s = I - dt * self.eps2_sq * self.laplacian
        b_s = s + dt * self.reaction_s(p, s)
        s_new = spsolve(A_s, b_s)
        
        return p_new, s_new
    
    def simulate_periodic(self, p0, s0, T, dt):
        """Симуляция с периодическим воздействием"""
        Nt = int(T / dt)
        
        p_history = np.zeros((Nt, self.Nx))
        s_history = np.zeros((Nt, self.Nx))
        times = np.zeros(Nt)
        r_history = np.zeros(Nt)  # положение контрастной структуры
        
        p, s = p0.copy(), s0.copy()
        
        for n in range(Nt):
            t = n * dt
            p, s = self.step_implicit_periodic(p, s, t, dt)
            p_history[n] = p
            s_history[n] = s
            times[n] = t
            
            # Находим положение контрастной структуры (где p ≈ 0.5)
            r_history[n] = self.find_transition_point(p)
            
            if n % 100 == 0:
                print(f"Step {n}/{Nt}, t={t:.2f}, r={r_history[n]:.3f}")
        
        return times, p_history, s_history, r_history
    
    def find_transition_point(self, p):
        """Находит точку перехода контрастной структуры"""
        # Ищем, где p пересекает среднее значение
        p_mean = (p.max() + p.min()) / 2
        crossings = np.where(np.diff(np.sign(p - p_mean)))[0]
        if len(crossings) > 0:
            return self.x[crossings[0]]
        else:
            return 0.5  # если не нашли, возвращаем середину

# Сравнение режимов α < 1, α = 1, α > 1
def compare_alpha_regimes():
    """Сравнивает три режима"""
    fig, axes = plt.subplots(3, 3, figsize=(18, 15))
    
    alphas = [0.5, 1.0, 1.5]  # α < 1, α = 1, α > 1
    titles = ['α < 1 (медленные настроения)', 
              'α = 1 (критический режим)',
              'α > 1 (быстрые настроения)']
    
    for i, (alpha, title) in enumerate(zip(alphas, titles)):
        print(f"\n--- Режим: {title} ---")
        
        model = PowerSocietyModelPeriodic(
            Nx=200, 
            eps1_sq=0.005,
            eps2_sq=0.2,
            alpha_parameter=alpha,
            period=20.0,
            amplitude=0.2
        )
        
        # Начальное условие - контрастная структура
        p0 = 0.3 + 0.4 * (1 + np.tanh((model.x - 0.5) / 0.05))
        s0 = 0.5 * np.ones(model.Nx)
        
        # Симуляция
        T = 100
        dt = 0.05
        times, p_hist, s_hist, r_hist = model.simulate_periodic(p0, s0, T, dt)
        
        # График 1: пространственно-временная диаграмма
        axes[i, 0].imshow(p_hist.T, aspect='auto', origin='lower',
                         extent=[0, T, 0, 1], cmap='RdBu_r')
        axes[i, 0].plot(times, r_hist, 'k-', linewidth=2, label='r(t)')
        axes[i, 0].set_xlabel('Время')
        axes[i, 0].set_ylabel('x')
        axes[i, 0].set_title(f'{title}: p(x,t)')
        axes[i, 0].legend()
        
        # График 2: движение точки перехода r(t)
        axes[i, 1].plot(times, r_hist, 'b-', linewidth=2)
        axes[i, 1].set_xlabel('Время')
        axes[i, 1].set_ylabel('r(t)')
        axes[i, 1].set_title('Положение контрастной структуры')
        axes[i, 1].grid(True)
        
        # График 3: фазовый портрет r(t) vs dr/dt
        dr_dt = np.gradient(r_hist, times)
        axes[i, 2].plot(r_hist, dr_dt, 'g-', alpha=0.7)
        axes[i, 2].set_xlabel('r')
        axes[i, 2].set_ylabel('dr/dt')
        axes[i, 2].set_title('Фазовый портрет')
        axes[i, 2].grid(True)
    
    plt.tight_layout()
    plt.savefig('alpha_regimes_comparison.png', dpi=150)
    plt.show()

# Запуск сравнения
compare_alpha_regimes()