# Рендер видео «Р.С.Ф.Г.Р. 1920–1975» на Android в Termux

Инструкция воспроизводит последний рендер: тот же сценарий, те же кадры, те же параметры кодирования
и та же нарезка на четыре части.

## 0. Что получится

| | |
|---|---|
| Сценарий | `scenario_rsfgr.json` — 35 событий, 1920–1975 |
| Кадр | 1920×1080, 30 к/с, 10 190 кадров = 5 мин 39,7 с, без звука |
| Мастер-файл | `out/rsfgr.mp4` — H.264 High, `-preset medium -crf 18`, yuv420p, ≈ 300 МБ |
| Части | 4 файла ≈ 28 МиБ: H.264 в два прохода, `-preset medium`, битрейт под 29 МиБ, `+faststart` |

Части режутся по кадрам ровно в начале перелёта к событию:

| Часть | Кадры | Длительность | Годы | Видеобитрейт |
|---|---|---|---|---|
| 1 | 0 – 2599 | 86,63 с | 1920 – 1929 | 2712 кбит/с |
| 2 | 2599 – 4844 | 74,83 с | 1929 – 1939 | 3144 кбит/с |
| 3 | 4844 – 7548 | 90,13 с | 1939 – 1956 | 2605 кбит/с |
| 4 | 7548 – 10190 | 88,07 с | 1958 – 1975 | 2667 кбит/с |

На одном и том же коде кадры совпадают с эталоном пиксель в пиксель (проверено в чистой папке).
В Termux могут быть другие версии cairo, freetype и x264, поэтому файлы выйдут визуально такими же,
но не байт в байт.

## 1. Что нужно

- **Termux из F-Droid или со страницы релизов на GitHub.** Версия из Google Play устарела, `pkg` в ней
  не работает.
- **Место: 1,5 ГБ свободно.** Распакованный пакет вместе с документами занимает ≈ 230 МБ. Мастер-файл
  весит ≈ 300 МБ, и на время склейки рядом лежат его куски, ещё ≈ 300 МБ. Части — ≈ 115 МБ.
- **Память: ≈ 0,75 ГБ на один рабочий процесс** рендера (замерено) плюс ≈ 0,2 ГБ на его ffmpeg.
  Отсюда число процессов `N`:

  | Свободная ОЗУ | `--workers` |
  |---|---|
  | 2–3 ГБ | 1–2 |
  | 4–6 ГБ | 3 |
  | 8 ГБ и больше | 4 (больше обычно не ускоряет: у телефонов мало «больших» ядер) |

- **Время.** На двух ядрах облачной машины выходило ≈ 0,95 с на кадр на процесс, то есть ≈ 85 минут
  при `--workers 2`. Для телефона оцените сами по шагу 6: `время ≈ 10190 × (с/кадр) / N × 1,1`.
- **Исходные изображения документов.** Это ваши оригиналы: 12 ранних картинок (`ChatGPT_Image_….png`,
  `karta_rsfgr_1.png`, `d96e790e-….png`) и архив `RSFGR_40-70s_1.zip` (33 картинки). Имена файлов
  неважны: подбор идёт по контрольной сумме.

## 2. Подготовка Termux

```sh
termux-setup-storage            # разрешить доступ к памяти: появится ~/storage/downloads
pkg update && pkg upgrade -y
pkg install -y python python-numpy python-pillow pycairo ffmpeg fontconfig-utils unzip
```

Проверка — команда должна напечатать `ok` без ошибок:

```sh
python -c "import numpy, cairo, PIL; print('ok')" && ffmpeg -hide_banner -encoders | grep -q libx264 && echo x264
```

Модуль cairo ставится пакетом `pycairo`, а не через `pip`. Геобиблиотеки (rasterio, shapely, pyproj)
для рендера **не нужны**: всё, что от них зависит, уже посчитано и лежит в пакете (`cache/`,
`cache/detail/`, `overlays/`, `out/overlay/`).

## 3. Пакет проекта

Положите `future_borders_src.zip` в «Загрузки» телефона и распакуйте:

```sh
cd ~
unzip -o ~/storage/downloads/future_borders_src.zip
cd ~/future_borders
```

Внутри: код, сценарии, шрифты, готовый кэш карты, слои (соляной пояс, Пояс Уэйта, Алтайская межа,
споровые облака 1947 г.), скрипты `make_docs.py` и `split_parts.py`.

## 4. Шрифты

Без них cairo молча подставит другой шрифт, и всё видео будет набрано не тем.

```sh
mkdir -p $PREFIX/share/fonts/rsfgr
cp fonts/*.ttf $PREFIX/share/fonts/rsfgr/
fc-cache -f
fc-list | grep -E "Old Standard|Oswald"
```

Должно быть пять строк: Old Standard TT (Regular, Italic, Bold) и Oswald (Medium, Bold). Если шрифт
не найден, рендер сам предупредит строкой `WARNING: font … is not installed`.

## 5. Документы

Скрипт копирует оригиналы в `docs_rsfgr/` под теми именами, которые ждёт сценарий. Ему можно передать
папки, отдельные файлы и zip-архивы в любом количестве:

```sh
python make_docs.py ~/storage/downloads/rsfgr_images ~/storage/downloads/RSFGR_40-70s_1.zip
```

Итог должен быть `docs_rsfgr: 45 of 45 in place`. Если чего-то не хватает, скрипт перечислит, какие
исходные файлы не найдены (столбец 3 в `docs_rsfgr_names.tsv`), и завершится с ошибкой. Его можно
запускать повторно и дособирать по частям.

## 6. Проверка перед долгим рендером

```sh
python render_archive.py --scenario scenario_rsfgr.json --plan | head -1
```

Ожидается `frames 10190 = 339.7 s`. Если число другое, сценарий не тот, и нарезка из шага 8
не совпадёт с эталоном.

Пробные кадры: 1947 г. со слоем споровых облаков, 1953 г. с Алтайской межой, 1974 г.:

```sh
python render_archive.py --scenario scenario_rsfgr.json --name rsfgr --preview 5650 6870 9800
cp out/rsfgr_preview_*.png ~/storage/downloads/
```

Посмотрите их в галерее. Каждая строка вывода показывает время на кадр
(`preview 5650 (hold, ev=21) 2.0 s`): по нему оцените общее время.

## 7. Рендер

Не давайте телефону заснуть и запускайте в фоне с журналом:

```sh
termux-wake-lock
nohup python render_archive.py --scenario scenario_rsfgr.json --name rsfgr --workers 2 > render.log 2>&1 &
tail -f render.log            # Ctrl+C прекращает только просмотр, рендер идёт дальше
```

`--workers` выберите по таблице из шага 1. Кадры делятся поровну между процессами, каждый пишет свой
кусок `out/rsfgr_seg_K.mp4` (libx264, `-preset medium -crf 18`, yuv420p, 30 к/с). В конце куски
склеиваются без перекодирования в `out/rsfgr.mp4` с `+faststart`, и журнал заканчивается строкой
`done: …/out/rsfgr.mp4`. Прогресс выводится каждые 100 кадров:
`[rsfgr_seg_0.mp4] 1700/5095 0.85 s/frame`.

Продолжения после обрыва нет: прерванный рендер запускается заново.

Если на Android 12 и новее процесс обрывается сигналом 9 (`[Process completed (signal 9)]` или
внезапный конец журнала), это системный ограничитель фоновых процессов. Что помогает:
- держать Termux на экране;
- включить в «Для разработчиков» пункт «Отключить ограничения для дочерних процессов»
  (Android 14 и новее);
- либо выполнить с компьютера
  `adb shell device_config put activity_manager max_phantom_processes 2147483647`.

Если процесс убит из-за памяти, уменьшите `--workers`.

## 8. Нарезка на части

```sh
python split_parts.py out/rsfgr.mp4 --scenario scenario_rsfgr.json \
    --at elbe drought pannonia --prefix rsfgr_1920-1975 --dry-run
```

Сухой прогон должен показать ровно границы и битрейты из таблицы в шаге 0. Потом то же без `--dry-run`:

```sh
python split_parts.py out/rsfgr.mp4 --scenario scenario_rsfgr.json \
    --at elbe drought pannonia --prefix rsfgr_1920-1975
```

Что делает скрипт:
- **Границы.** Находит по плану кадров начало перелёта к событиям `elbe` (1929), `drought` (1939)
  и `pannonia` (1958).
- **Обрезка.** Режет точно по кадру (`-ss` перед входом плюс `-frames:v`); проверено на эталоне.
- **Кодирование.** Каждую часть кодирует в два прохода: libx264, `-preset medium`, yuv420p, без звука,
  `+faststart`. Видеобитрейт = 29 · 8 · 1024 / длительность − 30 кбит/с.

Результат — `out/rsfgr_1920-1975_part1.mp4 … part4.mp4`, каждый ≈ 28 МиБ. Другой предел размера
задаётся ключом `--mib`, например `--mib 49`. Если нужен один файл без нарезки, берите сразу
`out/rsfgr.mp4`.

```sh
cp out/rsfgr_1920-1975_part*.mp4 ~/storage/downloads/
termux-wake-unlock
```

## 9. Сверка с эталоном

```sh
for f in out/rsfgr_1920-1975_part*.mp4; do
  ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$f"
done
```

Длительности должны быть 86.633333, 74.833333, 90.133333, 88.066667. Размеры — около 29,3–29,5 млн
байт: точные числа зависят от сборки x264.

## 10. Если что-то не так

| Симптом | Причина и решение |
|---|---|
| `ModuleNotFoundError: No module named 'cairo'` | `pkg install pycairo` |
| `No module named 'rasterio'` или `'shapely'` при рендере | Нет нужного файла в `cache/detail/`: папка не распаковалась или в сценарии изменили `camera` у события. Растр приближения для новой камеры строится только с геобиблиотеками (раздел 11) |
| `FileNotFoundError: docs_rsfgr/…` | Шаг 5 не дошёл до `45 of 45` |
| `WARNING: font …` или надписи «не тем» шрифтом | Шаг 4 |
| `frames` не 10190 | Сценарий изменён; заново посчитайте `--dry-run` нарезки |
| Процесс убит (signal 9), журнал оборвался | Шаг 7: ограничитель Android или нехватка памяти |
| `ffmpeg: not found` / нет `libx264` | `pkg install ffmpeg` (сборка Termux включает libx264) |

## 11. Если менять сценарий

- **Безопасно на телефоне.** Можно менять тексты, подписи, документы, длительности фаз (`pre`, `trans`,
  `hold`), цвета и состав государств (`ops`). Нужен только рендер.
- **Новая или изменённая `camera` у события с сильным приближением** требует растра приближения.
  Его строит `prep_details.py`, которому нужны rasterio и shapely, а также
  `../maps_extract/unified/unified_regions.geojson` и `../maps_extract/out/lakes_10m.geojson`.
  Проще сделать это на компьютере и перенести появившиеся файлы `cache/detail/*.npz`.
- **Слои.** `overlay_spores_1947.py` работает и в Termux после `pkg install python-scipy matplotlib`.
  `overlay_bands.py` и `overlay_altai_border_1953.py` требуют shapely и pyproj — их лучше запускать
  на компьютере.

### Полная пересборка данных карты (на компьютере)

Нужна, только если меняются сами границы или население. Раскладка папок — рядом друг с другом:

```
work/
  html-generated/     git clone https://github.com/USER/html-generated
  maps_extract/       скрипты из future_borders/maps_extract_scripts/
  future_borders/
```

```sh
pip install numpy shapely pyproj rasterio pycountry pycairo pillow
npm install mapshaper            # проверено с 0.6.121

cd work
python3 maps_extract/topo2geo.py html-generated/maps/data maps_extract/out
python3 maps_extract/build_unified.py maps_extract/out maps_extract/unified
python3 maps_extract/add_cities.py maps_extract/out maps_extract/unified

cd maps_extract/unified
mkdir -p ms
cp unified_countries.geojson ms/countries.geojson
cp unified_regions.geojson ms/regions.geojson
cp unified_cities.geojson ms/cities.geojson
npx mapshaper -i ms/countries.geojson ms/regions.geojson ms/cities.geojson combine-files \
  -each 'name=name_short || admin' target=countries \
  -o format=topojson quantization=100000 target=* unified-10m.topo.json

cd ../../future_borders
python3 prep.py ../maps_extract/unified/unified-10m.topo.json ../html-generated/webmap/assets/countries.json
python3 prep_details.py scenario_rsfgr.json
```

Имена файлов в `ms/` важны: из них получаются имена объектов TopoJSON (`countries`, `regions`,
`cities`). Команда mapshaper в таком виде воспроизводит эталонный `unified-10m.topo.json` один в один.
После пересборки данных скопируйте `cache/` на телефон целиком.
