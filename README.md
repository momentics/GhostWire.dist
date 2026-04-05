# GhostWire

**SOCKS5-to-masked HTTPS proxy with anti-DPI protection.**

GhostWire is a config-driven proxy library that tunnels SOCKS5 connections through masked HTTPS, providing DPI analysis resistance. It exposes a plain C FFI API for integration into C, C++, Python, Kotlin, Swift, and other languages.

---

## What is GhostWire?

GhostWire is a **binary library**, not a standalone application. It embeds into your projects and provides:

- **SOCKS5 proxy** — accepts standard SOCKS5 connections
- **masked HTTPS tunnel** — converts traffic to masked HTTPS for DPI bypass
- **Real-time statistics** — monitoring connections, traffic, and errors
- **Cross-platform** — Windows, Linux, macOS, Android, iOS

---

## Who is this repository for?

The **GhostWire.dist** repository is the public distribution channel for **prebuilt binary artifacts**. It does **not contain source code**.

Here you will find:

| Section | Description |
|---|---|
| [GitHub Releases](https://github.com/momentics/GhostWire.dist/releases) | Prebuilt binary files for all supported platforms |
| [`docs/abi-policy.md`](docs/abi-policy.md) | Full FFI C/C++ API documentation with examples for C, C++, Python |
| [`docs/platform-matrix.md`](docs/platform-matrix.md) | Supported platforms and architectures matrix |
| [`docs/LICENSE`](docs/LICENSE) | Licensing terms |
| [`install/`](install/) | Scripts for programmatic release downloading |

---

## Quick Start

### 1. Download a Release

Go to [Releases](https://github.com/momentics/GhostWire.dist/releases) and pick the latest version.

Or use the automated install scripts:

**PowerShell (Windows):**

```powershell
.\install\fetch.ps1 -Version 1.0.0 -Asset ghostwire-windows-x86_64.zip
```

**Bash (Linux/macOS):**

```bash
./install/fetch.sh 1.0.0 ghostwire-linux-x86_64.tar.gz
```

### 2. Link the Library

Extract the artifact and include `ghostwire.h` in your project. See [`docs/abi-policy.md`](docs/abi-policy.md) for examples.

**C (minimal example):**

```c
#include <stdio.h>
#include "ghostwire.h"

int main(void) {
    GwProxy* proxy = ghostwire_proxy_create_from_file("config.json");
    if (!proxy) return 1;

    ghostwire_proxy_start(proxy);
    printf("Proxy running on 127.0.0.1:1080\n");

    getchar();  /* Runs until you press Enter */

    ghostwire_proxy_stop(proxy);
    ghostwire_proxy_free(proxy);
    return 0;
}
```

**Python (ctypes):**

```python
import ctypes

lib = ctypes.CDLL("ghostwire.dll")  # or libghostwire.so / libghostwire.dylib
proxy = lib.ghostwire_proxy_create_from_file(b"config.json")
lib.ghostwire_proxy_start(proxy)
print("Proxy running!")
```

Full examples for C, C++, and Python are in [`docs/abi-policy.md`](docs/abi-policy.md).

### 3. Configure Telegram Desktop

Once GhostWire is running:

1. **Telegram Desktop → Settings → Advanced → Connection Type**
2. Select **SOCKS5**
3. Enter:
   - **Server:** `127.0.0.1`
   - **Port:** `1080` (or your port from `config.json`)
   - **Login / Password:** leave empty
4. Click **Save**

---

## Supported Platforms

| Platform | Architecture | Format | Status |
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

Details in [`docs/platform-matrix.md`](docs/platform-matrix.md).

---

## API Overview

The library exposes a **C API** via `ghostwire.h`:

| Function | Description |
|---|---|
| `ghostwire_proxy_create_from_file(path)` | Create proxy from config file |
| `ghostwire_proxy_start(proxy)` | Start SOCKS5 server |
| `ghostwire_proxy_stop(proxy)` | Stop SOCKS5 server |
| `ghostwire_proxy_free(proxy)` | Free resources |
| `ghostwire_proxy_is_running(proxy)` | Check if proxy is running |
| `ghostwire_proxy_get_stats(proxy, &out)` | Get statistics (connections, traffic, errors) |

All functions are `extern "C"` and safe to call from C++.

Full documentation with integration examples for **C**, **C++**, **Python**, **Android (JNI/Kotlin)**, and **iOS (Swift)** — see [`docs/abi-policy.md`](docs/abi-policy.md).

---

## Configuration

GhostWire operates alongside a `config.json` file that defines:

- SOCKS5 server address and port
- masked HTTPS connection parameters
- IP rotation settings
- Other anti-DPI protection options

Example `config.json` structure and all available options are described in the main library documentation.

---

## License

The library is distributed **free of charge** in binary form and may be used in personal and commercial projects.

**Allowed:**

- Freely distribute binary files
- Use in personal and commercial projects without additional fees

**Prohibited:**

- Reverse engineering, decompilation, disassembly
- Attempts to obtain source code
- Creating derivative works based on source code

Full license text — in [`docs/LICENSE`](docs/LICENSE).

---

## Repository Structure

```
.
├── README.md                 ← This file
├── docs/
│   ├── abi-policy.md         ← FFI API documentation with examples
│   ├── platform-matrix.md    ← Platform compatibility matrix
│   └── LICENSE               ← License terms
├── install/
│   ├── fetch.ps1             ← PowerShell script for downloading releases
│   └── fetch.sh              ← Bash script for downloading releases
└── manifests/                ← CI/CD metadata
```

---

## Questions & Feedback

For licensing inquiries, bug reports, and suggestions, please open an [Issue](https://github.com/momentics/GhostWire.dist/issues) or contact @momentics directly.
