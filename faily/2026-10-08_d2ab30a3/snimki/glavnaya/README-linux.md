# Eldamo: локальный запуск на Linux x64

Инструкция поднимает генератор сайта Eldamo (https://github.com/pfstrack/eldamo) на локальном веб-сервере Jetty. Рабочая связка: **JDK 8 x64 + Gradle 7.6.4 + Gretty 3.1.5 (Jetty 9.4)**.

> Оригинальный README репозитория устарел: он написан в 2015 году под Gradle 2.6 и старый плагин `jetty`, а `build.gradle` в 2022 году перевели на Gretty 4.0.0. В таком виде проект не запускается ни на одной системе (подробности в разделе «Почему не работает по оригинальному README»). Ниже — рабочий путь.

## 1. Что понадобится

| Что | Версия | Зачем |
|---|---|---|
| git, unzip, curl | любые | клонирование и установка |
| JDK | **8** (допустим 11) | компиляция и запуск. Нужен JDK, а не только JRE |
| Gradle | **7.6.4** | сборка |
| Свободная память | ≥ 1,5 ГБ | сервер держит в памяти разобранный XML-словарь |

Про версии:

- Gradle 7.6.4 запускается только на Java до 19 включительно. JDK 21, который сейчас стоит по умолчанию во многих дистрибутивах, для запуска Gradle не годится. Его не нужно удалять: достаточно поставить рядом JDK 8 и указать его в `JAVA_HOME`.
- Gradle из репозиториев дистрибутива обычно не той версии (часто очень старый). Ставьте 7.6.4 отдельно.

## 2. Установка JDK и Gradle

### Вариант А: SDKMAN (любой дистрибутив, без root)

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

sdk list java | grep -E '8\.0\..*-tem'      # посмотреть доступные сборки Temurin 8
sdk install java 8.0.<версия>-tem           # подставьте версию из списка
sdk install gradle 7.6.4
```

SDKMAN сам выставит `JAVA_HOME` и `PATH`.

### Вариант Б: пакеты дистрибутива + Gradle из архива

JDK 8.

Ubuntu (20.04, 22.04, 24.04):
```bash
sudo apt install openjdk-8-jdk-headless
```

Fedora:
```bash
sudo dnf install java-1.8.0-openjdk-devel
```

Debian 12 и новее JDK 8 в основных репозиториях не содержат. Там используйте вариант А или репозиторий Adoptium: https://adoptium.net/installation/linux/ .

Gradle 7.6.4 из архива:
```bash
curl -LO https://services.gradle.org/distributions/gradle-7.6.4-bin.zip
sudo unzip -q -d /opt gradle-7.6.4-bin.zip
```

Переменные окружения. Добавьте в `~/.bashrc` (путь к JDK подставьте свой, список установленных JDK: `ls /usr/lib/jvm`):
```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH="/opt/gradle-7.6.4/bin:$JAVA_HOME/bin:$PATH"
```

Затем `source ~/.bashrc`.

### Проверка

```bash
javac -version     # javac 1.8.0_xxx
gradle -v          # Gradle 7.6.4, JVM: 1.8.0_xxx
```

## 3. Клонирование

```bash
git clone https://github.com/pfstrack/eldamo.git
cd eldamo
```

## 4. Исправления в проекте

### Быстрый путь: патч

Положите `eldamo-run-fixes.patch` рядом и выполните из корня репозитория:

```bash
git apply /путь/к/eldamo-run-fixes.patch
git status --short     # изменены build.gradle и два .java-файла
```

Патч содержит все три правки ниже. Если применяете его, сразу переходите к разделу 5.

### 4.1. `build.gradle`: Gretty 3 вместо Gretty 4

Gretty 4.x работает только с Jetty 11 и Tomcat 10 (пространство имён `jakarta.servlet`), а код Eldamo написан на `javax.servlet`. Нужна ветка Gretty 3.x с Jetty 9.4.

Замените `build.gradle` целиком:

```gradle
plugins {
    id 'org.gretty' version '3.1.5'
}

apply plugin: 'java'
apply plugin: 'eclipse'
apply plugin: 'war'

sourceCompatibility = 1.8
version = '0.8.1'
compileJava.options.encoding = 'UTF-8'

repositories {
    mavenCentral()
}

dependencies {
    implementation group: 'net.sourceforge.saxon', name: 'saxon', version: '9.1.0.8'
    implementation group: 'net.sourceforge.saxon', name: 'saxon', version: '9.1.0.8', classifier: 's9api'
    implementation group: 'net.sourceforge.saxon', name: 'saxon', version: '9.1.0.8', classifier: 'dom'
    implementation group: 'net.sourceforge.saxon', name: 'saxon', version: '9.1.0.8', classifier: 'xpath'
    implementation group: 'javax.servlet', name: 'javax.servlet-api', version: '3.0.1'
    implementation group: 'junit', name: 'junit', version: '4.+'
}

gretty {
    servletContainer = 'jetty9.4'
    contextPath = '/eldamo'
    jvmArgs = ['-Xmx1024m']
}
```

### 4.2. `BufferedResponseWrapper.java`: методы Servlet 3.1

Jetty 9.4 приносит в компиляцию servlet-api 3.1, где у `ServletOutputStream` два новых абстрактных метода. Без правки сборка падает с ошибкой `does not override abstract method setWriteListener(javax.servlet.WriteListener)`.

В файле `src/main/java/xdb/layout/BufferedResponseWrapper.java` замените блок

```java
    private final ServletOutputStream sos = new ServletOutputStream() {

        @Override
        public void write(int b) throws IOException {
            baos.write(b);
        }
    };
```

на

```java
    private final ServletOutputStream sos = new ServletOutputStream() {

        @Override
        public void write(int b) throws IOException {
            baos.write(b);
        }

        @Override
        public boolean isReady() {
            return true;
        }

        @Override
        public void setWriteListener(javax.servlet.WriteListener writeListener) {
            throw new UnsupportedOperationException("Async I/O is not supported");
        }
    };
```

Сам класс приложением не используется (фильтр `LayoutFilter` в `web.xml` закомментирован), заглушки нужны только для компиляции.

### 4.3. `XQueryEngine.java`: URI модуля (на Linux необязательно)

На Linux проект работает и без этой правки: путь вида `/home/.../common.xq` сам по себе является допустимым URI. Но на Windows без неё ломаются почти все страницы `/content/...` (`Variable $lang-name has not been declared`). Если репозиторий будут собирать и на Windows, правку стоит внести: на Linux она ничего не меняет.

В файле `src/main/java/xdb/dom/XQueryEngine.java` (около строки 51) замените

```java
                src = new StreamSource(new FileInputStream(path), path);
```

на

```java
                src = new StreamSource(new FileInputStream(path), new java.io.File(path).toURI().toString());
```

## 5. Данные словаря

Приложение ищет файл строго в `src/main/webapp/data/eldamo-data.xml`. Шаг 5 оригинального README, где указан `src/main/webapp/eldamo-data.xml`, ошибочен.

```bash
cp -R src/data src/main/webapp
ls -l src/main/webapp/data/eldamo-data.xml
```

## 6. Запуск

```bash
gradle appRun
```

- Первый запуск долгий: Gradle скачивает Saxon, Jetty и плагин.
- Сервер готов, когда в логе появится:
  ```
  eldamo runs at:
    http://localhost:8080/eldamo
  ```
- Строка прогресса Gradle при этом застынет на `87% EXECUTING` с `> :appRun`. Это нормально: задача держит сервер, пока вы его не остановите.
- **Остановка:** любая клавиша в терминале («Press any key to stop the server»).
- Сервер слушает все интерфейсы (`0.0.0.0:8080`). Если на машине открыт файрвол, а доступ нужен только локально, ничего настраивать не нужно. Для доступа с других машин откройте порт 8080.

### Запуск на сервере без терминала

`appRun` останавливается нажатием клавиши, поэтому без терминала (через `nohup`, `screen`, systemd) используйте `appStart`. Он ждёт не клавишу, а команду `appStop`:

```bash
nohup gradle appStart > eldamo.log 2>&1 &    # запуск в фоне
gradle appStop                               # остановка, из любого терминала в папке проекта
```

Если нужен постоянно работающий сервис, проще собрать `war` (`gradle war`, файл появится в `build/libs/`) и положить его в отдельный Jetty 9.4 или Tomcat 9. Контейнеры Jetty 10+ и Tomcat 10+ не подойдут по той же причине, что и Gretty 4: они работают на `jakarta.servlet`. Учтите, что данные должны лежать в `data/` внутри развёрнутого приложения, а контейнер должен разворачивать `war` в каталог (приложение читает файлы через `getRealPath`).

## 7. Проверка

```bash
for u in languages/index.html language-pages/lang-q.html word-indexes/words-q.html references/index.html search/search.html; do
  curl -s -o /dev/null -w "$u %{http_code}\n" "http://localhost:8080/eldamo/content/$u"
done
```

Все адреса должны вернуть `200`. В браузере начните с http://localhost:8080/eldamo/ .

О каталоге `content`:

- На диске его нет и не будет. Адреса `/eldamo/content/...` обслуживает `DispatchServlet`: он собирает страницу на лету из XQuery-шаблонов `config/query-configs/*.xq` и данных `eldamo-data.xml`.
- У `/content/` нет индексной страницы. Адрес `http://localhost:8080/eldamo/content/` отвечает `No query for uri`, это нормально.
- Первый запрос к `/content/` может занять 10–20 секунд: словарь загружается при первом обращении (`NO_AUTOLOAD=true`). Крупные указатели, например квенийских слов, собираются несколько секунд.

## 8. Правка данных и сборка статичного сайта

- Gretty работает из копии `build/inplaceWebapp`, это видно в логе по строке с путём к `data`. Если после правки `src/main/webapp/data/eldamo-data.xml` изменения не появились, перезапустите сервер.
- Публикуемая версия сайта: http://localhost:8080/eldamo/pub/index.html . Статичный сайт, как на eldamo.org, получают обходом краулером, например:
  ```bash
  wget --mirror --convert-links --adjust-extension --page-requisites --no-parent \
       http://localhost:8080/eldamo/pub/index.html
  ```

## 9. Типичные ошибки

| Симптом | Причина | Что делать |
|---|---|---|
| `gradle: command not found` | Gradle не в `PATH` | раздел 2 |
| `Unsupported class file major version 65` или подобное при запуске Gradle | Gradle запущен на JDK 21+ | `JAVA_HOME` на JDK 8 |
| `Plugin [id: 'org.gretty', version: '4.0.0'] was not found` | не сделана правка 4.1 или старый Gradle | разделы 2 и 4.1 |
| `does not override abstract method setWriteListener` | не сделана правка 4.2 | раздел 4.2 |
| `Could not reserve enough space for object heap` / `OutOfMemoryError` | мало памяти | освободить память или поднять `-Xmx` в блоке `gretty` |
| `Address already in use` | порт 8080 занят | `ss -ltnp | grep 8080`, либо `httpPort = 8081` в блоке `gretty` |

## Почему не работает по оригинальному README

1. `gradle :jettyRun` с `org.gretty 4.0.0` поднимает Jetty 11 (`jakarta.servlet`), а приложение на `javax.servlet`.
2. Требования «Java 1.6+, Gradle 2.6+» не соответствуют `build.gradle`: Gretty 4 требует JDK 11+ и Gradle 6+.
3. В шаге 5 неверный путь к данным.
4. Резолвер XQuery-модулей не работает с путями Windows (правка 4.3); на Linux и macOS это не проявляется.
