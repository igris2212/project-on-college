# Сборка APK на Windows - Подробная инструкция

Buildozer работает только на Linux, но есть несколько способов собрать APK для Android на Windows!

## 🎯 Рекомендуемые методы для Windows

### Метод 1: Google Colab (Самый простой!) ⭐

**Преимущества**: Бесплатно, не требует установки, работает в браузере

#### Шаги:

1. **Откройте Google Colab**: https://colab.research.google.com/

2. **Создайте новый блокнот** и выполните следующие команды:

```python
# Ячейка 1: Установка Buildozer
!pip install buildozer
!pip install cython==0.29.33

# Установка зависимостей
!sudo apt-get update
!sudo apt-get install -y git zip unzip openjdk-17-jdk wget
!sudo apt-get install -y python3-pip build-essential git python3 python3-dev
!sudo apt-get install -y ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
!sudo apt-get install -y libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
!sudo apt-get install -y libgstreamer1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good
!sudo apt-get install -y autoconf libtool pkg-config

# Ячейка 2: Загрузка вашего проекта
from google.colab import files
import zipfile
import os

# Создайте ZIP архив вашей папки приложения и загрузите его
uploaded = files.upload()

# Распакуйте
for filename in uploaded.keys():
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('/content/app')

# Перейдите в папку
%cd /content/app

# Ячейка 3: Создание buildozer.spec (если его нет)
!buildozer init

# Ячейка 4: Сборка APK
!buildozer -v android debug

# Ячейка 5: Скачивание APK
from google.colab import files
import os

# Найти APK файл
apk_path = !find /content -name "*.apk"
if apk_path:
    print(f"APK найден: {apk_path[0]}")
    files.download(apk_path[0])
else:
    print("APK не найден")
```

3. **Подготовьте проект**:
   - Создайте ZIP архив папки `приложение`
   - Загрузите в Colab через ячейку 2

4. **Дождитесь сборки** (15-30 минут)

5. **Скачайте APK** - файл автоматически скачается в браузер

---

### Метод 2: WSL (Windows Subsystem for Linux) 💻

**Преимущества**: Полный контроль, работает локально

#### Установка WSL:

1. **Откройте PowerShell от имени администратора**:
```powershell
wsl --install
```

2. **Перезагрузите компьютер**

3. **Откройте Ubuntu** из меню Пуск

4. **Установите зависимости**:
```bash
sudo apt update
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt install -y libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
```

5. **Установите Buildozer**:
```bash
pip3 install buildozer cython==0.29.33
```

6. **Скопируйте проект в WSL**:
```bash
# В WSL терминале
cd ~
cp -r /mnt/c/Users/Техносмарт/Desktop/приложение ./
cd приложение
```

7. **Соберите APK**:
```bash
buildozer -v android debug
```

8. **Скопируйте APK обратно в Windows**:
```bash
cp bin/*.apk /mnt/c/Users/Техносмарт/Desktop/
```

---

### Метод 3: GitHub Actions (Автоматическая сборка) 🤖

**Преимущества**: Автоматизация, бесплатно для публичных репозиториев

#### Шаги:

1. **Создайте репозиторий на GitHub**

2. **Загрузите ваш проект**

3. **Создайте файл** `.github/workflows/build.yml`:

```yaml
name: Build APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y git zip unzip openjdk-17-jdk wget
        sudo apt-get install -y python3-pip build-essential git python3-dev
        sudo apt-get install -y ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
        sudo apt-get install -y libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
        pip install buildozer cython==0.29.33

    - name: Build APK
      run: |
        buildozer -v android debug

    - name: Upload APK
      uses: actions/upload-artifact@v2
      with:
        name: app-debug
        path: bin/*.apk
```

4. **Закоммитьте и запушьте**

5. **Перейдите в Actions** на GitHub

6. **Скачайте APK** из артефактов

---

### Метод 4: python-for-android (Продвинутый) 🔧

**Для опытных пользователей**

```bash
# В WSL или Git Bash
pip install python-for-android
p4a create --requirements=python3,kivy,kivymd --arch=arm64-v8a --name=reference --package=org.example.reference --version=1.0 --bootstrap=sdl2
```

---

## 🚀 Быстрый старт: Google Colab (Рекомендуется!)

### Пошаговая инструкция:

1. **Подготовьте проект**:
   - Откройте папку `C:\Users\Техносмарт\Desktop\приложение`
   - Выделите все файлы (main.py, data.json, requirements.txt, buildozer.spec)
   - Щелкните правой кнопкой → "Отправить" → "Сжатая ZIP-папка"
   - Назовите: `app.zip`

2. **Откройте готовый Colab блокнот**:
   - Перейдите на: https://colab.research.google.com/
   - Создайте новый блокнот
   - Скопируйте код ниже

3. **Скопируйте этот код в Colab**:

```python
# ========== ЯЧЕЙКА 1: Установка ==========
!pip install buildozer cython==0.29.33
!sudo apt-get update
!sudo apt-get install -y git zip unzip openjdk-17-jdk wget
!sudo apt-get install -y python3-pip build-essential git python3 python3-dev
!sudo apt-get install -y ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
!sudo apt-get install -y libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
!sudo apt-get install -y libgstreamer1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good
!sudo apt-get install -y autoconf libtool pkg-config

# ========== ЯЧЕЙКА 2: Загрузка проекта ==========
from google.colab import files
import zipfile
import os

print("📁 Загрузите ZIP архив вашего проекта...")
uploaded = files.upload()

for filename in uploaded.keys():
    print(f"📦 Распаковка {filename}...")
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('/content/app')

print("✅ Проект загружен!")

# ========== ЯЧЕЙКА 3: Настройка проекта ==========
%cd /content/app

# Проверяем наличие buildozer.spec
if not os.path.exists('buildozer.spec'):
    print("⚠️ buildozer.spec не найден, создаем...")
    !buildozer init
else:
    print("✅ buildozer.spec найден!")

# Показываем содержимое папки
!ls -la

# ========== ЯЧЕЙКА 4: Сборка APK ==========
print("🔨 Начинаем сборку APK...")
print("⏰ Это займет 15-30 минут, наберитесь терпения...")
!buildozer -v android debug

# ========== ЯЧЕЙКА 5: Скачивание APK ==========
from google.colab import files
import glob

print("🔍 Поиск APK файла...")
apk_files = glob.glob('/content/app/bin/*.apk')

if apk_files:
    apk_path = apk_files[0]
    print(f"✅ APK найден: {apk_path}")
    print("📥 Скачивание начинается...")
    files.download(apk_path)
    print("🎉 Готово! APK скачан!")
else:
    print("❌ APK не найден. Проверьте логи сборки выше.")
    print("📂 Содержимое bin/:")
    !ls -la bin/ 2>/dev/null || echo "Папка bin не найдена"
```

4. **Запустите ячейки по порядку**:
   - Нажмите на первую ячейку и нажмите Shift+Enter
   - Дождитесь выполнения
   - Переходите к следующей ячейке

5. **В ячейке 2** загрузите ваш `app.zip`

6. **Дождитесь сборки** в ячейке 4 (15-30 минут)

7. **APK автоматически скачается** после ячейки 5

---

## 📱 Установка APK на телефон

1. **Скопируйте APK** на телефон (через USB, облако, мессенджер)

2. **Разрешите установку** из неизвестных источников:
   - Настройки → Безопасность → Неизвестные источники

3. **Откройте APK** и установите

4. **Готово!** Приложение установлено

---

## ⚠️ Возможные проблемы

### Проблема: Сборка в Colab прерывается

**Решение**: 
- Colab имеет ограничение по времени (12 часов)
- Держите вкладку открытой
- Используйте Colab Pro для стабильности

### Проблема: APK не устанавливается на телефон

**Решение**:
- Проверьте версию Android (минимум Android 5.0)
- Включите установку из неизвестных источников
- Проверьте свободное место на телефоне

### Проблема: Приложение вылетает при запуске

**Решение**:
- Проверьте логи через `adb logcat`
- Убедитесь, что все зависимости указаны в buildozer.spec
- Проверьте разрешения в buildozer.spec

---

## 💡 Советы

1. **Используйте Google Colab** - самый простой способ для начинающих
2. **Сохраните блокнот Colab** - можно использовать повторно
3. **Тестируйте на эмуляторе** перед установкой на телефон
4. **Читайте логи** - они помогут найти ошибки

---

## 🔗 Полезные ссылки

- **Buildozer документация**: https://buildozer.readthedocs.io/
- **Kivy для Android**: https://kivy.org/doc/stable/guide/packaging-android.html
- **Google Colab**: https://colab.research.google.com/
- **WSL установка**: https://docs.microsoft.com/en-us/windows/wsl/install

---

## 📞 Альтернативные решения

### Онлайн-сервисы для сборки APK:
- **Replit** - онлайн IDE с поддержкой Linux
- **Gitpod** - облачная среда разработки
- **CodeSandbox** - для веб-приложений

### Локальные решения:
- **VirtualBox** с Ubuntu - полноценная виртуальная машина
- **Docker** - контейнеризация

---

> [!TIP]
> **Рекомендация**: Начните с Google Colab - это самый быстрый и простой способ получить APK без установки дополнительного ПО!

> [!IMPORTANT]
> Первая сборка может занять до 30 минут, так как Buildozer скачивает Android SDK, NDK и другие компоненты. Последующие сборки будут быстрее!
