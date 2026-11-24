def amplitude_equation_coefficients(J, eps1_sq, eps2_sq, k_c):
    """Вычисляет коэффициенты амплитудного уравнения"""
    J11, J12, J21, J22 = J[0,0], J[0,1], J[1,0], J[1,1]
    
    # Собственные векторы при k = k_c
    eigenval = (J11 + J22)/2 - k_c**2*(eps1_sq + eps2_sq)/2
    
    # Это упрощенная формула, полный вывод требует метода многих масштабов
    mu0 = eigenval  # инкремент
    
    # Коэффициент Ландау (требует нелинейных членов)
    # Для кубической нелинейности в исходной системе:
    g = 1.0  # нужен точный расчет из кубических членов
    
    # Диффузия амплитуды
    D = eps1_sq + eps2_sq
    
    return mu0, g, D

# Стационарная амплитуда
def stationary_amplitude(mu0, g):
    if mu0 > 0:
        A_st = np.sqrt(mu0/g)
        return A_st
    else:
        return 0

# Устойчивость
def stability_stationary(mu0, g, D, k):
    """Устойчивость стационарного паттерна к возмущениям"""
    A_st = stationary_amplitude(mu0, g)
    if A_st > 0:
        lambda_pert = -2*mu0 - D*k**2  # для возмущения exp(λt + ikX)
        return lambda_pert
    else:
        return mu0 - D*k**2