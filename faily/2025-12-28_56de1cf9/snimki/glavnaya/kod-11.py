def construct_regime_diagram():
    """
    Строит полную диаграмму режимов:
    - Область Тьюринга
    - Области для разных α
    - Резонансные зоны
    """
    
    # Параметры для сканирования
    alphas = np.linspace(0.3, 2.0, 40)
    deltas = np.logspace(0, 2.5, 40)  # δ = ε₂²/ε₁² от 1 до 300
    
    # Матрицы для хранения результатов
    has_turing = np.zeros((len(alphas), len(deltas)))
    regime_type = np.zeros((len(alphas), len(deltas)))
    # 0 - нет паттернов
    # 1 - вибрация (α<1 + Тьюринг)
    # 2 - подстройка (α>1 + Тьюринг)
    # 3 - хаос (α≈1 + Тьюринг)
    
    # Фиксированные параметры
    a, mu = 1.0, 0.8
    beta_val = 2.0
    alpha_interact = 0.5
    eps1_sq = 0.01
    
    for i, alpha_param in enumerate(alphas):
        for j, delta in enumerate(deltas):
            eps2_sq = delta * eps1_sq
            
            # Проверяем условия Тьюринга
            try:
                p_st, s_st = find_steady_state(a, alpha_interact, beta_val, mu)
                if p_st > 0 and s_st > 0:
                    J = jacobian(p_st, s_st, a, alpha_interact, beta_val, mu)
                    is_turing, k_c = check_turing_conditions(J, eps1_sq, eps2_sq)
                    
                    if is_turing:
                        has_turing[i, j] = 1
                        
                        # Классификация режима
                        if alpha_param < 0.9:
                            regime_type[i, j] = 1  # вибрация
                        elif alpha_param > 1.1:
                            regime_type[i, j] = 2  # подстройка
                        else:
                            regime_type[i, j] = 3  # хаос
            except:
                pass
    
    # Визуализация
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Диаграмма 1: Где есть Тьюринг
    im1 = axes[0].contourf(np.log10(deltas), alphas, has_turing,
                           levels=[0, 0.5, 1], colors=['white', 'lightblue'])
    axes[0].set_xlabel('log₁₀(δ = ε₂²/ε₁²)')
    axes[0].set_ylabel('α (скорость настроений)')
    axes[0].set_title('Область паттернов Тьюринга')
    axes[0].axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='α=1')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Диаграмма 2: Типы режимов
    im2 = axes[1].contourf(np.log10(deltas), alphas, regime_type,
                           levels=[0, 0.5, 1.5, 2.5, 3.5],
                           colors=['white', 'lightgreen', 'orange', 'red'])
    axes[1].set_xlabel('log₁₀(δ = ε₂²/ε₁²)')
    axes[1].set_ylabel('α')
    axes[1].set_title('Типы динамических режимов')
    
    # Легенда
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='white', label='Нет паттернов'),
        Patch(facecolor='lightgreen', label='Вибрация (α<1)'),
        Patch(facecolor='orange', label='Подстройка (α>1)'),
        Patch(facecolor='red', label='Хаос (α≈1)')
    ]
    axes[1].legend(handles=legend_elements, loc='upper left')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('regime_diagram.png', dpi=200)
    plt.show()
    
    return alphas, deltas, has_turing, regime_type

# Построить диаграмму
alphas, deltas, has_turing, regime_type = construct_regime_diagram()