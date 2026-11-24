class HistoricalDataAnalyzer:
    """Анализ исторических данных для оценки параметров модели"""
    
    def __init__(self):
        self.data = {}
    
    def load_data(self, country, years, centralization_index, protest_index):
        """
        Загружает исторические данные
        
        centralization_index: индекс централизации власти (0-1)
        protest_index: индекс протестной активности (0-1)
        """
        self.data[country] = {
            'years': np.array(years),
            'centralization': np.array(centralization_index),
            'protests': np.array(protest_index)
        }
    
    def estimate_alpha(self, country):
        """Оценивает параметр α из данных"""
        years = self.data[country]['years']
        centr = self.data[country]['centralization']
        
        # Оценка характерного времени изменения
        # через автокорреляцию
        autocorr = np.correlate(centr - centr.mean(), 
                               centr - centr.mean(), 
                               mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr /= autocorr[0]
        
        # Находим время корреляции (где автокорр. падает до e^-1)
        tau_corr_idx = np.where(autocorr < 1/np.e)[0]
        if len(tau_corr_idx) > 0:
            tau_corr = years[tau_corr_idx[0]] - years[0]
        else:
            tau_corr = years[-1] - years[0]
        
        # Оценка α: если изменения медленные, то α < 1
        # Используем эвристику: α ≈ 1 / log(tau_corr)
        alpha_est = 1.0 / max(np.log(tau_corr + 1), 1)
        
        return alpha_est, tau_corr
    
    def estimate_diffusion_ratio(self, country):
        """Оценивает соотношение δ = ε₂²/ε₁²"""
        # Анализ пространственной корреляции протестов vs централизации
        protests = self.data[country]['protests']
        centr = self.data[country]['centralization']
        
        # Если протесты быстро распространяются (высокая дисперсия),
        # то ε₂² большое
        var_protests = np.var(protests)
        var_centr = np.var(centr)
        
        # Эвристическая оценка
        delta_est = max(var_protests / (var_centr + 1e-6), 1.0)
        
        return delta_est
    
    def fit_model_to_data(self, country):
        """Подгоняет параметры модели к историческим данным"""
        alpha_est, tau = self.estimate_alpha(country)
        delta_est = self.estimate_diffusion_ratio(country)
        
        print(f"\n--- Оценка параметров для {country} ---")
        print(f"α ≈ {alpha_est:.3f} (время корреляции: {tau:.1f} лет)")
        print(f"δ = ε₂²/ε₁² ≈ {delta_est:.1f}")
        
        # Классификация режима
        if alpha_est < 0.8:
            regime = "Инерционный (α < 1)"
        elif alpha_est > 1.2:
            regime = "Реактивный (α > 1)"
        else:
            regime = "Критический (α ≈ 1)"
        
        print(f"Режим: {regime}")
        
        return {
            'alpha': alpha_est,
            'delta': delta_est,
            'tau_correlation': tau,
            'regime': regime
        }

# Пример: данные для СССР (упрощенные)
analyzer = HistoricalDataAnalyzer()

# Данные 1950-1990 (индексы условные, 0-1)
years_ussr = list(range(1950, 1991))
centralization_ussr = [0.9]*20 + [0.85]*10 + [0.7]*5 + [0.5]*6  # усреднённо
protests_ussr = [0.1]*30 + [0.3]*5 + [0.6]*6

analyzer.load_data('USSR', years_ussr, centralization_ussr, protests_ussr)
params_ussr = analyzer.fit_model_to_data('USSR')

# Данные для США (упрощенные)
years_usa = list(range(1960, 2021))
centralization_usa = 0.5 + 0.1*np.sin(np.arange(len(years_usa))/4)  # колебания
protests_usa = 0.3 + 0.2*np.random.randn(len(years_usa)).cumsum()/10

analyzer.load_data('USA', years_usa, centralization_usa, protests_usa)
params_usa = analyzer.fit_model_to_data('USA')