# Eldamo: локальный запуск на Windows 7 x64

Инструкция поднимает генератор сайта Eldamo (https://github.com/pfstrack/eldamo) на локальном веб-сервере Jetty. Проверено на Windows 7 x64 со связкой **Temurin JDK 8 (x64) + Gradle 7.6.4 + Gretty 3.1.5 (Jetty 9.4)**.

> Оригинальный README репозитория устарел: он написан в 2015 году под Gradle 2.6 и старый плагин `jetty`, а `build.gradle` в 2022 году перевели на Gretty 4.0.0. В таком виде проект не запускается ни на одной системе (подробности в разделе «Почему не работает по оригинальному README»). Ниже — рабочий путь.

## 1. Что понадобится

| Что | Версия | Зачем |
|---|---|---|
| Git | любая | клонировать репозиторий |
| JDK | **Temurin 8, x64, именно JDK** | компиляция и запуск. JRE не подходит: в ней нет `javac` |
| Gradle | **7.6.4** | сборка. Gradle 8+ не ставить |
| Свободная память | ≥ 1,5 ГБ | сервер держит в памяти разобранный XML-словарь |

Почему такие версии на Windows 7:

- JDK 17 и 21 Windows 7 официально не поддерживают, установщики новых версий часто отказываются ставиться. JDK 8 работает без вопросов. JDK 11 тоже допустим, но проверен был именно JDK 8.
- Нужна **64-битная** Java. 32-битная (в `java -version` видно `Client VM`) часто не может выделить серверу 1 ГБ кучи.
- Старые Java 6/7 и ранние апдейты Java 8 не договариваются по TLS 1.2 с Maven Central и порталом плагинов Gradle, и загрузка зависимостей падает.

## 2. Установка JDK

1. Скачайте с https://adoptium.net/temurin/releases/ : **Version 8**, **Windows**, **x64**, **JDK**, файл `.msi`.
2. В установщике включите **Set JAVA_HOME variable** и **Add to PATH**.
3. Откройте **новое** окно PowerShell и проверьте:

```powershell
javac -version            # javac 1.8.0_xxx
java -version             # должно быть "64-Bit Server VM"
$env:JAVA_HOME            # путь к папке JDK
```

Если `java -version` показывает старую 32-битную Java (`Client VM`), это не страшно: Gradle берёт Java из `JAVA_HOME`. Главное, чтобы `JAVA_HOME` указывал на новый JDK.

## 3. Установка Gradle

1. Скачайте `gradle-7.6.4-bin.zip` со страницы https://gradle.org/releases/ . Удобнее браузером: PowerShell на Windows 7 по умолчанию плохо работает с современным HTTPS.
2. Распакуйте, например, в `D:\gradle\gradle-7.6.4`.
3. Добавьте Gradle в пользовательский `PATH` **насовсем**:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";D:\gradle\gradle-7.6.4\bin", "User")
```

4. Закройте PowerShell, откройте новый и проверьте:

```powershell
gradle -v
```

В выводе должны быть `Gradle 7.6.4` и в строке `JVM` ваш 64-битный JDK 8.

Замечания:

- Команда вида `$env:Path = "...;$env:Path"` действует только в текущем окне. В новом окне будет `gradle : The term 'gradle' is not recognized`.
- `setx` для `PATH` не используйте: он молча обрезает значение длиннее 1024 символов.
- Если имя пользователя Windows написано кириллицей, Gradle может спотыкаться о путь `C:\Users\Имя\.gradle`. Тогда задайте кэш в ASCII-пути:
  ```powershell
  [Environment]::SetEnvironmentVariable("GRADLE_USER_HOME", "D:\gradle-home", "User")
  ```

## 4. Клонирование

```powershell
cd D:\github
git clone https://github.com/pfstrack/eldamo.git
cd eldamo
```

## 5. Три исправления в проекте

### 5.1. `build.gradle`: Gretty 3 вместо Gretty 4

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

### 5.2. `BufferedResponseWrapper.java`: методы Servlet 3.1

Jetty 9.4 приносит в компиляцию servlet-api 3.1, где у `ServletOutputStream` два новых абстрактных метода. Без правки сборка падает с ошибкой `does not override abstract method setWriteListener(javax.servlet.WriteListener)`.

В файле `src\main\java\xdb\layout\BufferedResponseWrapper.java` замените блок

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

### 5.3. `XQueryEngine.java`: URI модуля (обязательно на Windows)

Без этой правки на Windows открывается только указатель источников, а все остальные страницы `/content/...` выдают ошибки вида:

```
XQuery static error in #...> <title>Eldamo : {$lang-name}#: Variable $lang-name has not been declared
One or more static errors were reported during query analysis
```

Причина в резолвере модулей: он передаёт Saxon'у путь `D:\...\common.xq` как URI, а такой URI Saxon не разбирает. Импорт `common.xq` срывается, вместе с ним обрывается разбор пролога запроса.

В файле `src\main\java\xdb\dom\XQueryEngine.java` (около строки 51) замените

```java
                src = new StreamSource(new FileInputStream(path), path);
```

на

```java
                src = new StreamSource(new FileInputStream(path), new java.io.File(path).toURI().toString());
```

## 6. Данные словаря

Приложение ищет файл строго в `src\main\webapp\data\eldamo-data.xml`. Шаг 5 оригинального README, где указан `src/main/webapp/eldamo-data.xml`, ошибочен.

```powershell
Copy-Item -Recurse src\data src\main\webapp
Test-Path src\main\webapp\data\eldamo-data.xml     # должно быть True
```

В `cmd.exe` вместо этого: `xcopy src\data src\main\webapp\data /E /I`.

## 7. Запуск

```powershell
gradle appRun
```

- Первый запуск долгий: Gradle скачивает Saxon, Jetty и плагин.
- Брандмауэр Windows спросит разрешение для Java: сервер слушает порт 8080. Для работы на `localhost` можно разрешить только частные сети.
- Сервер готов, когда в логе появится:
  ```
  eldamo runs at:
    http://localhost:8080/eldamo
  ```
- Строка прогресса Gradle при этом застынет на `87% EXECUTING` с `> :appRun`. Это нормально: задача держит сервер, пока вы его не остановите.
- **Остановка:** любая клавиша в окне PowerShell («Press any key to stop the server»).

## 8. Проверка

Откройте http://localhost:8080/eldamo/ и пройдите по ссылкам. Контрольные адреса:

```
http://localhost:8080/eldamo/content/languages/index.html
http://localhost:8080/eldamo/content/language-pages/lang-q.html
http://localhost:8080/eldamo/content/word-indexes/words-q.html
http://localhost:8080/eldamo/content/references/index.html
http://localhost:8080/eldamo/content/search/search.html
```

О каталоге `content`:

- На диске его нет и не будет. Адреса `/eldamo/content/...` обслуживает `DispatchServlet`: он собирает страницу на лету из XQuery-шаблонов `config\query-configs\*.xq` и данных `eldamo-data.xml`.
- У `/content/` нет индексной страницы. Адрес `http://localhost:8080/eldamo/content/` отвечает `No query for uri`, это нормально.
- Первый запрос к `/content/` может занять 10–20 секунд: словарь загружается при первом обращении (`NO_AUTOLOAD=true`). Крупные указатели, например квенийских слов, собираются несколько секунд.

## 9. Правка данных и сборка статичного сайта

- Gretty работает из копии `build\inplaceWebapp`, это видно в логе по строке с путём к `data`. Если после правки `src\main\webapp\data\eldamo-data.xml` изменения не появились, перезапустите `gradle appRun`.
- Публикуемая версия сайта: http://localhost:8080/eldamo/pub/index.html . Её обходят веб-краулером (HTTrack, `wget --mirror` и т. п.), чтобы получить статичный сайт, как на eldamo.org.

## 10. Типичные ошибки

| Симптом | Причина | Что делать |
|---|---|---|
| `gradle : The term 'gradle' is not recognized` | Gradle не в `PATH` или задан только для старого окна | раздел 3, открыть новое окно |
| `javac : The term 'javac' is not recognized` | установлена JRE, а не JDK | раздел 2 |
| `Plugin [id: 'org.gretty', version: '4.0.0'] was not found` или сбой загрузки | старый Gradle или старая Java без TLS 1.2 | Gradle 7.6.4 + свежий JDK 8 |
| `PKIX path building failed`, `handshake_failure` | старая Java или антивирус/прокси подменяет сертификаты | свежий JDK 8, проверить прокси |
| `does not override abstract method setWriteListener` | не сделана правка 5.2 | раздел 5.2 |
| `Variable $lang-name has not been declared` | не сделана правка 5.3 | раздел 5.3 |
| `Could not reserve enough space for object heap` | 32-битная Java | поставить 64-битный JDK |
| `Address already in use` / порт 8080 занят | предыдущий сервер не остановлен или порт занят другой программой | закрыть старое окно, либо добавить `httpPort = 8081` в блок `gretty` |

## Почему не работает по оригинальному README

1. `gradle :jettyRun` с `org.gretty 4.0.0` поднимает Jetty 11 (`jakarta.servlet`), а приложение на `javax.servlet`.
2. Требования «Java 1.6+, Gradle 2.6+» не соответствуют `build.gradle`: Gretty 4 требует JDK 11+ и Gradle 6+.
3. В шаге 5 неверный путь к данным.
4. Резолвер XQuery-модулей не работает с путями Windows (правка 5.3). Автор работает на macOS, поэтому проблема у него не проявляется.
