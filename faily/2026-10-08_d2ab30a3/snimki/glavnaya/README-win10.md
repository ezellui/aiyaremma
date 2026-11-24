# Eldamo: локальный запуск на Windows 10 x64

Инструкция поднимает генератор сайта Eldamo (https://github.com/pfstrack/eldamo) на локальном веб-сервере Jetty. Рабочая связка: **Temurin JDK 8 (x64) + Gradle 7.6.4 + Gretty 3.1.5 (Jetty 9.4)**. Она проверена на Windows 7 x64 и без изменений годится для Windows 10.

> Оригинальный README репозитория устарел: он написан в 2015 году под Gradle 2.6 и старый плагин `jetty`, а `build.gradle` в 2022 году перевели на Gretty 4.0.0. В таком виде проект не запускается ни на одной системе (подробности в разделе «Почему не работает по оригинальному README»). Ниже — рабочий путь.

## 1. Что понадобится

| Что | Версия | Зачем |
|---|---|---|
| Git | любая | клонировать репозиторий |
| JDK | **Temurin 8 x64** (допустим 11) | компиляция и запуск. Нужен именно JDK: в JRE нет `javac` |
| Gradle | **7.6.4** | сборка |
| Свободная память | ≥ 1,5 ГБ | сервер держит в памяти разобранный XML-словарь |

Про версии:

- **Не ставьте JDK 21 и новее для этой сборки.** Gradle 7.6.4 запускается только на Java до 19 включительно, а Gradle 8 хуже работает с Gretty 3. Если у вас уже стоит свежий JDK, это не мешает: поставьте рядом JDK 8 и направьте на него `JAVA_HOME` (см. ниже).
- Gradle из пакетных менеджеров может оказаться другой версии. Ставьте именно 7.6.4.

## 2. Установка JDK

Через winget (есть в Windows 10 начиная с 1809 при установленном «App Installer»):

```powershell
winget install EclipseAdoptium.Temurin.8.JDK
```

Или вручную: https://adoptium.net/temurin/releases/ → **Version 8**, **Windows**, **x64**, **JDK**, `.msi`. В установщике включите **Set JAVA_HOME variable** и **Add to PATH**.

Откройте **новое** окно PowerShell и проверьте:

```powershell
javac -version            # javac 1.8.0_xxx
$env:JAVA_HOME            # путь к папке JDK 8
```

Если на машине несколько JDK и `JAVA_HOME` указывает не на восьмёрку, поправьте его для пользователя:

```powershell
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-8.0.xxx-hotspot", "User")
```

Путь замените на свой. После этого откройте новое окно.

## 3. Установка Gradle

```powershell
New-Item -ItemType Directory -Force D:\gradle | Out-Null
Invoke-WebRequest https://services.gradle.org/distributions/gradle-7.6.4-bin.zip -OutFile D:\gradle\gradle-7.6.4-bin.zip
Expand-Archive D:\gradle\gradle-7.6.4-bin.zip -DestinationPath D:\gradle
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";D:\gradle\gradle-7.6.4\bin", "User")
```

Закройте PowerShell, откройте новый и проверьте:

```powershell
gradle -v
```

В выводе должны быть `Gradle 7.6.4` и в строке `JVM` ваш JDK 8.

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
- Брандмауэр Windows спросит разрешение для Java: сервер слушает порт 8080. Для работы на `localhost` достаточно разрешить частные сети.
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
| `Unsupported class file major version 65` или подобное при запуске Gradle | `JAVA_HOME` указывает на JDK 21+ | направить `JAVA_HOME` на JDK 8 |
| `Plugin [id: 'org.gretty', version: '4.0.0'] was not found` | не сделана правка 5.1 или старый Gradle | разделы 3 и 5.1 |
| `PKIX path building failed` | антивирус или корпоративный прокси подменяет сертификаты | проверить прокси, добавить его сертификат в JDK |
| `does not override abstract method setWriteListener` | не сделана правка 5.2 | раздел 5.2 |
| `Variable $lang-name has not been declared` | не сделана правка 5.3 | раздел 5.3 |
| `Address already in use` / порт 8080 занят | предыдущий сервер не остановлен или порт занят другой программой | закрыть старое окно, либо добавить `httpPort = 8081` в блок `gretty` |

## Почему не работает по оригинальному README

1. `gradle :jettyRun` с `org.gretty 4.0.0` поднимает Jetty 11 (`jakarta.servlet`), а приложение на `javax.servlet`.
2. Требования «Java 1.6+, Gradle 2.6+» не соответствуют `build.gradle`: Gretty 4 требует JDK 11+ и Gradle 6+.
3. В шаге 5 неверный путь к данным.
4. Резолвер XQuery-модулей не работает с путями Windows (правка 5.3). Автор работает на macOS, поэтому проблема у него не проявляется.
