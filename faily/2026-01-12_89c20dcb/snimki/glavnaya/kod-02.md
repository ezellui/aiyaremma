## 🔄 Используемые переводчики

Система использует несколько сервисов с fallback:
1. **Google Translate** (через @vitalets/google-translate-api)
2. **HuggingFace Translation Models** (через REST API)
3. **LibreTranslate** (опционально, self-hosted)

При недоступности одного сервиса автоматически переключается на следующий.

## 🧹 Обслуживание

### Очистка базы данных
```bash
npm run cleanup