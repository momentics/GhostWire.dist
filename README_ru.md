# GhostWire

**Anti-DPI protection for Telegram.**

GhostWire — это конфигурируемый прокси-сервер, который преобразует SOCKS5-соединения в трафик Telegram, обеспечивая защиту от анализа трафика (anti-DPI). Библиотека предоставляет FFI C/C++ API для интеграции в проекты на C, C++, Python, Kotlin, Swift и других языках.

---

## Что такое GhostWire?

GhostWire — это **бинарная библиотека**, а не самостоятельное приложение. Она встраивается в ваши проекты и предоставляет:

- **SOCKS5 proxy** — принимает стандартные SOCKS5-соединения
- **Туннель** — преобразует трафик для обхода DPI
- **Статистику в реальном времени** — мониторинг подключений, трафика и ошибок
- **Кроссплатформенность** — Windows, Linux, macOS, Android, iOS

---

## Для кого этот репозиторий?

Репозиторий **GhostWire.dist** — это публичный канал распространения **готовых бинарных артефактов**. Он **не содержит исходный код** библиотеки.

Здесь вы найдёте:

| Раздел | Описание |
|---|---|
| [GitHub Releases](https://github.com/momentics/GhostWire.dist/releases) | Готовые бинарные файлы для всех поддерживаемых платформ |
| [`docs/abi-policy.md`](docs/abi-policy.md) | Полная документация по FFI C/C++ API с примерами для C, C++, Python |
| [`docs/platform-matrix.md`](docs/platform-matrix.md) | Матрица поддерживаемых платформ и архитектур |
| [`docs/LICENSE`](docs/LICENSE) | Лицензионное соглашение |
| [`install/`](install/) | Скрипты для программного скачивания релизов |

---

## Быстрый старт

### 1. Скачайте релиз

Перейдите на страницу [Releases](https://github.com/momentics/GhostWire.dist/releases) и выберите последнюю версию.

Или используйте скрипты автоматической установки:

**PowerShell (Windows):**

```powershell
.\install\fetch.ps1 -Version 1.0.0 -Asset ghostwire-windows-x86_64.zip
```

**Bash (Linux/macOS):**

```bash
./install/fetch.sh 1.0.0 ghostwire-linux-x86_64.tar.gz
```

### 2. Подключите библиотеку

Распакуйте артефакт и подключите `ghostwire.h` к вашему проекту. Примеры — в [`docs/abi-policy.md`](docs/abi-policy.md).

**C (минимальный пример):**

```c
#include <stdio.h>
#include "ghostwire.h"

int main(void) {
    GwProxy* proxy = ghostwire_proxy_create_from_file("config.json");
    if (!proxy) return 1;

    ghostwire_proxy_start(proxy);
    printf("Proxy running on 127.0.0.1:1080\n");

    getchar();  /* Работает, пока не нажмёте Enter */

    ghostwire_proxy_stop(proxy);
    ghostwire_proxy_free(proxy);
    return 0;
}
```

**Python (ctypes):**

```python
import ctypes

lib = ctypes.CDLL("ghostwire.dll")  # или libghostwire.so / libghostwire.dylib
proxy = lib.ghostwire_proxy_create_from_file(b"config.json")
lib.ghostwire_proxy_start(proxy)
print("Proxy running!")
```

Полные примеры для C, C++ и Python — в [`docs/abi-policy.md`](docs/abi-policy.md).

### 3. Настройте Telegram Desktop

После запуска GhostWire:

1. **Telegram Desktop → Settings → Advanced → Connection Type**
2. Выберите **SOCKS5**
3. Укажите:
   - **Server:** `127.0.0.1`
   - **Port:** `1080` (или ваш порт из `config.json`)
   - **Login / Password:** оставьте пустыми
4. Нажмите **Save**

---

## Поддерживаемые платформы

| Платформа | Архитектура | Формат | Статус |
|---|---|---|---|
| **Windows** | x86_64 | `.dll` + `.lib` | ✅ |
| **Linux** | x86_64 | `.so` | ✅ |
| **macOS** | x86_64 | `.dylib` | ✅ |
| **macOS** | aarch64 (Apple Silicon) | `.dylib` | ✅ |
| **Android** | arm64-v8a | `.so` | ✅ |
| **Android** | armeabi-v7a | `.so` | ✅ |
| **Android** | x86_64 | `.so` | ✅ |
| **Android** | x86 | `.so` | ✅ |
| **iOS** | arm64 (device) | `.a` | ✅ |
| **iOS** | arm64 (simulator) | `.a` | ✅ |
| **iOS** | x86_64 (simulator) | `.a` | ✅ |

Подробности — в [`docs/platform-matrix.md`](docs/platform-matrix.md).

---

## API Overview

Библиотека предоставляет **C API** через заголовочный файл `ghostwire.h`:

| Функция | Описание |
|---|---|
| `ghostwire_proxy_create_from_file(path)` | Создать прокси из файла конфигурации |
| `ghostwire_proxy_start(proxy)` | Запустить SOCKS5-сервер |
| `ghostwire_proxy_stop(proxy)` | Остановить SOCKS5-сервер |
| `ghostwire_proxy_free(proxy)` | Освободить ресурсы |
| `ghostwire_proxy_is_running(proxy)` | Проверить, работает ли прокси |
| `ghostwire_proxy_get_stats(proxy, &out)` | Получить статистику (подключения, трафик, ошибки) |

Все функции безопасны для вызова из C++ (`extern "C"`).

Полная документация с примерами интеграции для **C**, **C++**, **Python**, **Android (JNI/Kotlin)** и **iOS (Swift)** — в [`docs/abi-policy.md`](docs/abi-policy.md).

---

## Конфигурация

GhostWire работает в связке с файлом `config.json`, который определяет:

- Адрес и порт SOCKS5-сервера
- Параметры и Настройка анти-DPI защиты

Пример структуры `config.json` и все доступные опции описаны в основной документации к библиотеке.

---

## Лицензия

Библиотека распространяется **бесплатно** в бинарном виде и может использоваться в личных и коммерных проектах.

**Что разрешено:**

- ✅ Свободно распространять бинарные файлы
- ✅ Использовать в личных и коммерческих проектах без дополнительных отчислений

**Что запрещено:**

- ❌ Реверс-инжиниринг, декомпиляция, дизассемблирование
- ❌ Попытки получения исходного кода
- ❌ Создание производных работ на основе исходного кода

Полный текст лицензии — в [`docs/LICENSE`](docs/LICENSE).

---

## Структура репозитория

```
.
├── README.md                 ← Этот файл
├── docs/
│   ├── abi-policy.md         ← Документация по FFI API с примерами
│   ├── platform-matrix.md    ← Матрица платформ
│   └── LICENSE               ← Лицензия
├── install/
│   ├── fetch.ps1             ← PowerShell-скрипт для скачивания релизов
│   └── fetch.sh              ← Bash-скрипт для скачивания релизов
└── manifests/                ← Метаданные для CI/CD
```

---

## Вопросы и обратная связь

По вопросам лицензирования, баг-репортам и предложениям обращайтесь через [Issues](https://github.com/momentics/GhostWire.dist/issues) или напрямую к @momentics.
