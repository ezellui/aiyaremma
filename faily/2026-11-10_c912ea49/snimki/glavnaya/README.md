# ТПМ-2 — тенгварская пишущая машинка на челноке Хаммонда, редакция 0.9.3

Полный комплект проекта: исходники документа и модели, собранная модель (STL, рендеры, сборочные листы), интерактивная страница и проектный документ.

## Что где

| Путь | Что это |
|---|---|
| `tpm2-design-0.9.3.pdf` | проектный документ (собранный `main.pdf`) |
| `main.tex`, `preamble.tex` | исходник документа (XeLaTeX) |
| `Makefile` | сборка всего: модель → таблицы → страница → PDF |
| `data/` | раскладка, клавиатура, исходные таблицы |
| `fonts/` | Alcarin Tengwar (знаки литер), DejaVu Sans Bold (номера и служебные знаки на клавишах) с лицензиями |
| `tools/` | скрипты литер и FDM-проб (`stamps.py`, `fdmsim.py`, …) |
| `tools/model/` | компоновочная модель на python/manifold3d: детали (`parts.py`), спуск (`escape.py`), литерные блоки (`typeblocks.py`), проверки (`checks.py`, `scenarios.py`, `contacts.py`, `strike.py`), сборка (`build.py`), выгрузка для страницы (`webexport.py`) |
| `tools/web/` | исходники страницы (`page.html`, `viewer.js`, `transcribe.js`, `viewer.css`, `build_page.py`) и сверка страницы с моделью (`compare_model.py`) |
| `gen/model/stl/` | детали для печати: `NNN_bom__name.stl`, номер выдавлен на детали |
| `gen/model/renders/` | рендеры, сечения удара, сборочные листы `asm_*.png` |
| `gen/model/tpm2_assembly.glb` | вся машинка одним файлом glTF |
| `gen/model/printable.json`, `assembly.json` | перечень печатных деталей и состав сборочных листов |
| `gen/*.tex`, `gen/*.json` | таблицы и замеры, которые генерирует модель для документа |
| `gen/web/` | страница в упакованном виде (как опубликована) |
| `gen/web-plain/` | та же страница с неупакованной геометрией (как в `html-generated/tpm/`) |
| `stl/` | пробные отпечатки литер для FDM |

## Сборка

Нужны python 3 с `manifold3d`, `shapely`, `numpy`, `python-fcl`, `fonttools`, `matplotlib`, `pillow` и XeLaTeX.

```
python3 -I tools/model/build.py gen/model gen   # модель, STL, проверки (около 20 минут)
make                                             # таблицы, страница, PDF
make web-plain                                   # страница с неупакованной геометрией
```

`make` пересобирает модель, если какой-нибудь файл в `tools/model/` новее `gen/model/model.json`.
Сверка страницы с моделью (нужны playwright с chromium и three.js r128 локально):

```
python3 tools/web/compare_model.py gen/web-plain/tpm2-model.html THREE_MIN_JS ORBIT_CONTROLS_JS
```

## Состояние на 0.9.3

- 837 деталей, 232 уникальные печатные формы;
- проверки модели: 0 пересечений в покое и во всех сценариях, 58 касаний из 58, удар — 86 литер из 86;
- 0.9.3 меняет только страницу, геометрия та же, что в 0.9.2.
