# Псевдокод
Nx = 1000  # точек по x
Nt = 10000  # временных шагов

# Адаптивная сетка в области контрастной структуры
x_grid = adaptive_mesh(Nx, r_estimated)

for n in range(Nt):
    # Полунеявная схема для диффузии
    p_new = solve_implicit(ε₁², p, s, ...)
    s_new = solve_implicit(ε₂², p, s, ...)
    
    # Явный шаг для реакции
    p_new += dt * F_p(p_new, s_new, x, ε^α * t)
    s_new += dt * F_s(p_new, s_new, x, ε^α * t)
    
    # Обновление положения ступеньки
    r = find_transition(p_new)