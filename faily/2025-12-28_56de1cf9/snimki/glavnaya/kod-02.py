import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

def find_steady_state(a, alpha, beta, mu):
    """Находит стационарное состояние"""
    def equations(vars):
        p, s = vars
        eq1 = p*(a - p) - alpha*p*s
        eq2 = beta*p**2*s - mu*s
        return [eq1, eq2]
    
    # Ищем нетривиальное решение
    p_init = a/2
    s_init = 1.0
    sol = fsolve(equations, [p_init, s_init])
    return sol

def jacobian(p, s, a, alpha, beta, mu):
    """Вычисляет матрицу Якоби"""
    J11 = a - 2*p - alpha*s
    J12 = -alpha*p
    J21 = 2*beta*p*s
    J22 = beta*p**2 - mu
    return np.array([[J11, J12], [J21, J22]])

def check_turing_conditions(J, eps1_sq, eps2_sq):
    """Проверяет условия Тьюринга"""
    J11, J12 = J[0,0], J[0,1]
    J21, J22 = J[1,0], J[1,1]
    
    trace = J11 + J22
    det = J11*J22 - J12*J21
    
    cond1 = trace < 0  # Устойчивость при k=0
    cond2 = det > 0    # Устойчивость при k=0
    cond3 = J11*eps2_sq + J22*eps1_sq > 0  # Условие на диффузию
    
    discriminant = (J11*eps2_sq - J22*eps1_sq)**2 - 4*eps1_sq*eps2_sq*J12*J21
    cond4 = discriminant > 0  # Реальное k_c
    
    if all([cond1, cond2, cond3, cond4]):
        k_c_sq = (J11*eps2_sq + J22*eps1_sq)/(2*eps1_sq*eps2_sq) + \
                 np.sqrt(discriminant)/(2*eps1_sq*eps2_sq)
        return True, np.sqrt(k_c_sq)
    else:
        return False, None

# Сканирование пространства параметров
alphas = np.linspace(0.1, 2, 50)
betas = np.linspace(0.5, 5, 50)
a, mu = 1.0, 0.8
eps1_sq, eps2_sq = 0.01, 0.5

turing_region = np.zeros((len(alphas), len(betas)))
k_c_values = np.zeros((len(alphas), len(betas)))

for i, alpha in enumerate(alphas):
    for j, beta in enumerate(betas):
        try:
            p, s = find_steady_state(a, alpha, beta, mu)
            if p > 0 and s > 0:
                J = jacobian(p, s, a, alpha, beta, mu)
                is_turing, k_c = check_turing_conditions(J, eps1_sq, eps2_sq)
                if is_turing:
                    turing_region[i, j] = 1
                    k_c_values[i, j] = k_c
        except:
            pass

# Визуализация
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.contourf(betas, alphas, turing_region, levels=[0, 0.5, 1], 
             colors=['white', 'lightblue'])
plt.xlabel('β (активация общества)')
plt.ylabel('α (подавление власти)')
plt.title('Область существования паттернов Тьюринга')
plt.colorbar(label='Паттерны есть')

plt.subplot(1, 2, 2)
plt.contourf(betas, alphas, 2*np.pi/k_c_values, levels=20)
plt.xlabel('β')
plt.ylabel('α')
plt.title('Длина волны паттерна λ_c')
plt.colorbar(label='λ_c')

plt.tight_layout()
plt.savefig('turing_parameter_space.png', dpi=150)
plt.show()