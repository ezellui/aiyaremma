import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

class PowerSocietyModel:
    """Модель власть-общество с паттернами Тьюринга"""
    
    def __init__(self, Nx=200, L=1.0, eps1_sq=0.01, eps2_sq=0.5,
                 alpha=0.5, beta=2.0, mu=0.8, a=1.0):
        self.Nx = Nx
        self.L = L
        self.dx = L / (Nx - 1)
        self.x = np.linspace(0, L, Nx)
        
        # Параметры
        self.eps1_sq = eps1_sq
        self.eps2_sq = eps2_sq
        self.alpha = alpha
        self.beta = beta
        self.mu = mu
        self.a = a
        
        # Матрица лапласиана (для неявной схемы)
        self.laplacian = self._build_laplacian()
        
    def _build_laplacian(self):
        """Строит матрицу лапласиана с граничными условиями Неймана"""
        Nx = self.Nx
        dx = self.dx
        
        # Трёхдиагональная матрица
        main_diag = -2 * np.ones(Nx)
        off_diag = np.ones(Nx - 1)
        
        # Граничные условия: dp/dx = 0
        main_diag[0] = -1
        main_diag[-1] = -1
        off_diag[0] = 1
        off_diag[-1] = 1
        
        L = diags([off_diag, main_diag, off_diag], 
                  [-1, 0, 1], format='csr') / dx**2
        return L
    
    def reaction_p(self, p, s):
        """Реакционный член для власти"""
        return p * (self.a - p) - self.alpha * p * s
    
    def reaction_s(self, p, s):
        """Реакционный член для общественной активности"""
        return self.beta * p**2 * s - self.mu * s
    
    def step_implicit(self, p, s, dt):
        """Полунеявный шаг (IMEX схема)"""
        Nx = self.Nx
        
        # Неявный шаг для диффузии
        # (I - dt*D*Laplacian) * p_new = p_old + dt*Reaction(p_old, s_old)
        
        # Для p
        I = diags([1.0]*Nx, 0, format='csr')
        A_p = I - dt * self.eps1_sq * self.laplacian
        b_p = p + dt * self.reaction_p(p, s)
        p_new = spsolve(A_p, b_p)
        
        # Для s
        A_s = I - dt * self.eps2_sq * self.laplacian
        b_s = s + dt * self.reaction_s(p, s)
        s_new = spsolve(A_s, b_s)
        
        return p_new, s_new
    
    def simulate(self, p0, s0, T, dt):
        """Симуляция на время T с шагом dt"""
        Nt = int(T / dt)
        
        # Массивы для сохранения
        p_history = np.zeros((Nt, self.Nx))
        s_history = np.zeros((Nt, self.Nx))
        times = np.zeros(Nt)
        
        p, s = p0.copy(), s0.copy()
        
        for n in range(Nt):
            p, s = self.step_implicit(p, s, dt)
            p_history[n] = p
            s_history[n] = s
            times[n] = n * dt
            
            if n % 100 == 0:
                print(f"Step {n}/{Nt}, t={n*dt:.2f}")
        
        return times, p_history, s_history
    
    def initial_condition_random(self, p_mean=0.5, s_mean=0.5, noise=0.1):
        """Случайное начальное условие"""
        p0 = p_mean + noise * (2*np.random.rand(self.Nx) - 1)
        s0 = s_mean + noise * (2*np.random.rand(self.Nx) - 1)
        return p0, s0
    
    def initial_condition_perturbation(self, p_steady, s_steady, k_mode, amplitude=0.1):
        """Начальное условие с модой k"""
        p0 = p_steady + amplitude * np.cos(k_mode * self.x)
        s0 = s_steady + amplitude * np.cos(k_mode * self.x)
        return p0, s0

# Пример использования
model = PowerSocietyModel(Nx=200, eps1_sq=0.01, eps2_sq=0.5)

# Начальное условие
p0, s0 = model.initial_condition_random(p_mean=0.5, s_mean=0.5, noise=0.05)

# Симуляция
T = 100
dt = 0.01
times, p_hist, s_hist = model.simulate(p0, s0, T, dt)

# Визуализация
plt.figure(figsize=(14, 10))

# Пространственно-временная диаграмма для p
plt.subplot(3, 2, 1)
plt.imshow(p_hist.T, aspect='auto', origin='lower', 
           extent=[0, T, 0, 1], cmap='RdBu_r')
plt.colorbar(label='p(x,t)')
plt.xlabel('Время')
plt.ylabel('x')
plt.title('Эволюция власти p(x,t)')

# Пространственно-временная диаграмма для s
plt.subplot(3, 2, 2)
plt.imshow(s_hist.T, aspect='auto', origin='lower',
           extent=[0, T, 0, 1], cmap='YlOrRd')
plt.colorbar(label='s(x,t)')
plt.xlabel('Время')
plt.ylabel('x')
plt.title('Эволюция активности s(x,t)')

# Финальное распределение
plt.subplot(3, 2, 3)
plt.plot(model.x, p_hist[-1], 'b-', linewidth=2, label='p(x)')
plt.plot(model.x, s_hist[-1], 'r-', linewidth=2, label='s(x)')
plt.xlabel('x')
plt.ylabel('Значение')
plt.title(f'Распределение в момент t={T}')
plt.legend()
plt.grid(True)

# Фурье-анализ финального состояния
plt.subplot(3, 2, 4)
p_fft = np.abs(np.fft.fft(p_hist[-1] - p_hist[-1].mean()))
k_fft = np.fft.fftfreq(model.Nx, model.dx) * 2 * np.pi
plt.plot(k_fft[:model.Nx//2], p_fft[:model.Nx//2], 'b-', linewidth=2)
plt.xlabel('Волновое число k')
plt.ylabel('|F(k)|')
plt.title('Спектр паттерна власти')
plt.grid(True)

# Временная эволюция в разных точках
plt.subplot(3, 2, 5)
points = [0, model.Nx//4, model.Nx//2, 3*model.Nx//4, model.Nx-1]
for pt in points:
    plt.plot(times, p_hist[:, pt], label=f'x={model.x[pt]:.2f}')
plt.xlabel('Время')
plt.ylabel('p(x,t)')
plt.title('Временная динамика власти')
plt.legend()
plt.grid(True)

# Фазовая плоскость p-s в средней точке
plt.subplot(3, 2, 6)
mid = model.Nx // 2
plt.plot(p_hist[:, mid], s_hist[:, mid], 'b-', alpha=0.5)
plt.plot(p_hist[0, mid], s_hist[0, mid], 'go', markersize=10, label='Начало')
plt.plot(p_hist[-1, mid], s_hist[-1, mid], 'ro', markersize=10, label='Конец')
plt.xlabel('p (власть)')
plt.ylabel('s (активность)')
plt.title(f'Фазовый портрет в точке x={model.x[mid]:.2f}')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('simulation_results.png', dpi=150)
plt.show()