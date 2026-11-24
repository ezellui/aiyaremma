class PowerSocietyModel2D:
    """Двумерная модель с гексагональными паттернами"""
    
    def __init__(self, Nx=100, Ny=100, Lx=1.0, Ly=1.0, **params):
        self.Nx, self.Ny = Nx, Ny
        self.Lx, self.Ly = Lx, Ly
        self.dx, self.dy = Lx/(Nx-1), Ly/(Ny-1)
        self.x = np.linspace(0, Lx, Nx)
        self.y = np.linspace(0, Ly, Ny)
        self.X, self.Y = np.meshgrid(self.x, self.y)
        
        # Параметры (как в 1D)
        self.eps1_sq = params.get('eps1_sq', 0.01)
        self.eps2_sq = params.get('eps2_sq', 0.5)
        self.alpha = params.get('alpha', 0.5)
        self.beta = params.get('beta', 2.0)
        self.mu = params.get('mu', 0.8)
        self.a = params.get('a', 1.0)
    
    def laplacian_2d(self, u):
        """Вычисляет лапласиан функции u(x,y)"""
        lapl = np.zeros_like(u)
        
        # Внутренние точки
        lapl[1:-1, 1:-1] = (
            (u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[:-2, 1:-1]) / self.dx**2 +
            (u[1:-1, 2:] - 2*u[1:-1, 1:-1] + u[1:-1, :-2]) / self.dy**2
        )
        
        # Граничные условия Неймана (зеркальное отражение)
        lapl[0, :] = lapl[1, :]
        lapl[-1, :] = lapl[-2, :]
        lapl[:, 0] = lapl[:, 1]
        lapl[:, -1] = lapl[:, -2]
        
        return lapl
    
    def step_euler(self, p, s, dt):
        """Явный метод Эйлера (для демонстрации)"""
        # Диффузия
        dp_diff = self.eps1_sq * self.laplacian_2d(p)
        ds_diff = self.eps2_sq * self.laplacian_2d(s)
        
        # Реакция
        dp_reac = p * (self.a - p) - self.alpha * p * s
        ds_reac = self.beta * p**2 * s - self.mu * s
        
        # Обновление
        p_new = p + dt * (dp_diff + dp_reac)
        s_new = s + dt * (ds_diff + ds_reac)
        
        return p_new, s_new
    
    def simulate_2d(self, p0, s0, T, dt):
        """Симуляция 2D модели"""
        Nt = int(T / dt)
        
        p, s = p0.copy(), s0.copy()
        
        # Сохраняем каждые save_every шагов
        save_every = max(1, Nt // 100)
        saved_times = []
        saved_p = []
        saved_s = []
        
        for n in range(Nt):
            p, s = self.step_euler(p, s, dt)
            
            if n % save_every == 0:
                saved_times.append(n * dt)
                saved_p.append(p.copy())
                saved_s.append(s.copy())
                print(f"Step {n}/{Nt}, t={n*dt:.2f}")
        
        return saved_times, saved_p, saved_s
    
    def visualize_2d(self, p, s, title=""):
        """Визуализация 2D паттернов"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Власть p
        im1 = axes[0].contourf(self.X, self.Y, p, levels=20, cmap='RdBu_r')
        axes[0].set_title(f'Власть p(x,y) - {title}')
        axes[0].set_xlabel('x')
        axes[0].set_ylabel('y')
        plt.colorbar(im1, ax=axes[0])
        
        # Активность s
        im2 = axes[1].contourf(self.X, self.Y, s, levels=20, cmap='YlOrRd')
        axes[1].set_title(f'Активность s(x,y) - {title}')
        axes[1].set_xlabel('x')
        axes[1].set_ylabel('y')
        plt.colorbar(im2, ax=axes[1])
        
        # Комбинация
        combined = p - s
        im3 = axes[2].contourf(self.X, self.Y, combined, levels=20, cmap='PiYG')
        axes[2].set_title(f'p - s - {title}')
        axes[2].set_xlabel('x')
        axes[2].set_ylabel('y')
        plt.colorbar(im3, ax=axes[2])
        
        plt.tight_layout()
        return fig

# Пример: формирование гексагональных паттернов
model_2d = PowerSocietyModel2D(Nx=100, Ny=100, eps1_sq=0.01, eps2_sq=0.3)

# Начальное условие: случайный шум
p0_2d = 0.5 + 0.05 * np.random.randn(model_2d.Ny, model_2d.Nx)
s0_2d = 0.5 + 0.05 * np.random.randn(model_2d.Ny, model_2d.Nx)

# Симуляция
times_2d, p_hist_2d, s_hist_2d = model_2d.simulate_2d(p0_2d, s0_2d, T=50, dt=0.01)

# Визуализация финального состояния
model_2d.visualize_2d(p_hist_2d[-1], s_hist_2d[-1], title="t=50")
plt.savefig('2d_hexagonal_pattern.png', dpi=150)