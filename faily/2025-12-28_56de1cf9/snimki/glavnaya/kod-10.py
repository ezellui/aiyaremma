class PowerSocietyModelStochastic(PowerSocietyModel):
    """Модель с шумом (флуктуациями)"""
    
    def __init__(self, *args, noise_strength_p=0.01, noise_strength_s=0.01, **kwargs):
        super().__init__(*args, **kwargs)
        self.noise_p = noise_strength_p
        self.noise_s = noise_strength_s
    
    def step_stochastic(self, p, s, dt):
        """Шаг с аддитивным шумом"""
        # Детерминированная часть
        p_det, s_det = self.step_implicit(p, s, dt)
        
        # Стохастическая часть (винеровский процесс)
        noise_p = self.noise_p * np.sqrt(dt) * np.random.randn(self.Nx)
        noise_s = self.noise_s * np.sqrt(dt) * np.random.randn(self.Nx)
        
        p_new = p_det + noise_p
        s_new = s_det + noise_s
        
        # Обрезаем отрицательные значения
        p_new = np.maximum(p_new, 0)
        s_new = np.maximum(s_new, 0)
        
        return p_new, s_new
    
    def simulate_ensemble(self, p0, s0, T, dt, n_realizations=10):
        """Симуляция ансамбля траекторий"""
        Nt = int(T / dt)
        
        # Массивы для всех реализаций
        all_p = np.zeros((n_realizations, Nt, self.Nx))
        all_s = np.zeros((n_realizations, Nt, self.Nx))
        all_r = np.zeros((n_realizations, Nt))
        
        for n_real in range(n_realizations):
            print(f"Реализация {n_real+1}/{n_realizations}")
            
            p, s = p0.copy(), s0.copy()
            
            for n in range(Nt):
                p, s = self.step_stochastic(p, s, dt)
                all_p[n_real, n] = p
                all_s[n_real, n] = s
                all_r[n_real, n] = self.find_transition_point(p)
        
        return all_p, all_s, all_r
    
    def analyze_ensemble(self, all_r, times):
        """Анализ ансамбля: среднее и дисперсия"""
        mean_r = all_r.mean(axis=0)
        std_r = all_r.std(axis=0)
        
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        # Все траектории
        for n in range(all_r.shape[0]):
            plt.plot(times, all_r[n], 'b-', alpha=0.3, linewidth=0.5)
        # Среднее
        plt.plot(times, mean_r, 'r-', linewidth=3, label='Среднее')
        plt.fill_between(times, mean_r - std_r, mean_r + std_r,
                        alpha=0.3, color='red', label='±σ')
        plt.xlabel('Время')
        plt.ylabel('r(t)')
        plt.title('Ансамбль траекторий r(t)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(times, std_r, 'g-', linewidth=2)
        plt.xlabel('Время')
        plt.ylabel('σ(r)')
        plt.title('Дисперсия положения')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('stochastic_ensemble.png', dpi=150)
        
        return mean_r, std_r

# Пример: влияние шума на устойчивость паттернов
model_stoch = PowerSocietyModelStochastic(
    Nx=200, 
    eps1_sq=0.01, 
    eps2_sq=0.3,
    noise_strength_p=0.01,
    noise_strength_s=0.02
)

p0 = 0.3 + 0.4 * (1 + np.tanh((model_stoch.x - 0.5) / 0.05))
s0 = 0.5 * np.ones(model_stoch.Nx)

T, dt = 50, 0.05
times = np.arange(0, T, dt)
all_p, all_s, all_r = model_stoch.simulate_ensemble(p0, s0, T, dt, n_realizations=20)

mean_r, std_r = model_stoch.analyze_ensemble(all_r, times)