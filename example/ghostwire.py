#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GhostWire Python FFI Wrapper

Config-driven Anti-DPI Telegram proxy wrapper for the GhostWire DLL/SO.
"""

import ctypes
import os
import sys
from ctypes import (
    c_void_p, c_char_p, c_bool, c_uint64, c_int,
    Structure, POINTER, byref,
)
from typing import Optional
from dataclasses import dataclass
from enum import IntEnum


FRIENDLY_FEATURE_LINES = (
    "",
)


class ProxyState(IntEnum):
    """Coarse GhostWire proxy state returned by FFI."""
    OFFLINE = 0
    ONLINE = 1
    DEGRADED = 2


class ProxyStats(Structure):
    """FFI-safe proxy statistics structure"""
    _fields_ = [
        ("running", c_bool),
        ("active_connections", c_uint64),
        ("total_connections", c_uint64),
        ("websocket_active", c_uint64),
        ("bytes_received", c_uint64),
        ("bytes_sent", c_uint64),
        ("errors", c_uint64),
        ("ip_rotations", c_uint64),
        # Enhanced metrics
        ("media_connections", c_uint64),
        ("uptime_secs", c_uint64),
        ("peak_active_connections", c_uint64),
        ("rotation_success", c_uint64),
    ]

    def __repr__(self):
        return (
            f"ProxyStats(running={self.running}, "
            f"active={self.active_connections}, total={self.total_connections}, "
            f"ws_active={self.websocket_active}, "
            f"rx={self.bytes_received}, tx={self.bytes_sent}, "
            f"errors={self.errors}, rotations={self.ip_rotations}, "
            f"media={self.media_connections}, "
            f"uptime={self.uptime_secs}s, peak={self.peak_active_connections}, "
            f"rot_ok={self.rotation_success})"
        )


@dataclass
class ProxyStatsDataclass:
    """User-friendly proxy statistics"""
    running: bool
    active_connections: int
    total_connections: int
    websocket_active: int
    bytes_received: int
    bytes_sent: int
    errors: int
    ip_rotations: int
    # Enhanced metrics
    media_connections: int
    uptime_secs: int
    peak_active_connections: int
    rotation_success: int


def _find_library() -> str:
    """Find the library file in the local directory"""
    if sys.platform == "win32":
        lib_name = "ghostwire.dll"
    elif sys.platform == "darwin":
        lib_name = "libghostwire.dylib"
    else:
        lib_name = "libghostwire.so"

    # Look only in the local examples directory (copied by build.bat)
    local_path = os.path.join(os.path.dirname(__file__), lib_name)
    if os.path.exists(local_path):
        return os.path.abspath(local_path)

    if sys.platform == "win32":
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        candidate_paths = [
            os.path.join(repo_root, "target", "x86_64-pc-windows-msvc", "release", lib_name),
            os.path.join(repo_root, "target", "release", lib_name),
        ]
        for path in candidate_paths:
            if os.path.exists(path):
                return path

    return lib_name


class GhostWire:
    """
    GhostWire Python wrapper — config-driven anti-DPI proxy.

    All configuration loaded from config.json:
      - Data center endpoints (IPs, WebSocket URLs)
      - IP detection ranges (Telegram IP -> DC mapping)
      - Timeouts, buffer sizes, anti-DPI settings
      - Unified TLS+HTTP fingerprint profiles, TLS obfuscation, timing jitter
      - Traffic morphing for provider-facing WebSocket traffic

    Example usage:
        gw = GhostWire(config_path="config.json")
        gw.start()
        # Configure Telegram: Settings → Advanced → Connection Type → SOCKS5
        # Server: 127.0.0.1, Port: (from config.json), Login/Password: (empty)
        # ... Telegram works through proxy ...
        gw.stop()
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        config_json: Optional[str] = None,
        library_path: Optional[str] = None,
    ):
        """
        Initialize GhostWire proxy.

        Args:
            config_path: Path to config.json file (preferred)
            config_json: Config as JSON string (alternative to file)
            library_path: Override library auto-detection

        One of config_path or config_json must be provided.
        """
        self._lib = None
        self._proxy = None
        self._has_version_export = False
        self._has_features_export = False

        if config_path is None and config_json is None:
            # Default: look for config.json next to this file
            config_path = os.path.join(os.path.dirname(__file__), "config.json")

        self._config_path = config_path
        self._config_json = config_json
        self._library_path = library_path or _find_library()

        self._load_library()
        self._create_proxy()

    def _load_library(self):
        """Load the dynamic library"""
        try:
            self._lib = ctypes.CDLL(self._library_path)
        except OSError as e:
            raise RuntimeError(
                f"Failed to load library {self._library_path}: {e}\n"
                f"Build it first with: build.bat"
            )

        self._register_functions()

    def _register_functions(self):
        """Register C function signatures"""
        # Proxy lifecycle
        self._lib.ghostwire_proxy_create.restype = c_void_p
        self._lib.ghostwire_proxy_create.argtypes = [c_char_p]

        self._lib.ghostwire_proxy_create_from_file.restype = c_void_p
        self._lib.ghostwire_proxy_create_from_file.argtypes = [c_char_p]

        self._lib.ghostwire_proxy_free.restype = None
        self._lib.ghostwire_proxy_free.argtypes = [c_void_p]

        self._lib.ghostwire_proxy_start.restype = c_int
        self._lib.ghostwire_proxy_start.argtypes = [c_void_p]

        self._lib.ghostwire_proxy_stop.restype = None
        self._lib.ghostwire_proxy_stop.argtypes = [c_void_p]

        self._lib.ghostwire_proxy_get_state.restype = c_int
        self._lib.ghostwire_proxy_get_state.argtypes = [c_void_p]

        self._lib.ghostwire_proxy_get_stats.restype = None
        self._lib.ghostwire_proxy_get_stats.argtypes = [c_void_p, POINTER(ProxyStats)]

        # Info functions
        version_fn = getattr(self._lib, "ghostwire_version", None)
        if version_fn is not None:
            version_fn.restype = c_char_p
            version_fn.argtypes = []
            self._has_version_export = True

        features_fn = getattr(self._lib, "ghostwire_features", None)
        if features_fn is not None:
            features_fn.restype = c_char_p
            features_fn.argtypes = []
            self._has_features_export = True

    def _create_proxy(self):
        """Create proxy instance from config"""
        if self._config_path:
            if not os.path.exists(self._config_path):
                raise FileNotFoundError(
                    f"Config file not found: {self._config_path}"
                )
            self._proxy = self._lib.ghostwire_proxy_create_from_file(
                self._config_path.encode('utf-8')
            )
        elif self._config_json:
            self._proxy = self._lib.ghostwire_proxy_create(
                self._config_json.encode('utf-8')
            )

        if not self._proxy:
            raise RuntimeError(
                "Failed to create proxy — check config.json for errors"
            )

    def start(self) -> bool:
        """
        Start the SOCKS5 proxy.

        Returns:
            True if started successfully
        """
        if not self._proxy:
            raise RuntimeError("Proxy not created")

        result = self._lib.ghostwire_proxy_start(self._proxy)
        if result != 0:
            raise RuntimeError(f"Failed to start proxy (error {result})")
        return True

    def stop(self):
        """Stop the proxy"""
        if self._proxy:
            self._lib.ghostwire_proxy_stop(self._proxy)

    def get_state(self) -> ProxyState:
        """Get coarse proxy state: OFFLINE, ONLINE, or DEGRADED."""
        if not self._proxy:
            return ProxyState.OFFLINE
        return ProxyState(self._lib.ghostwire_proxy_get_state(self._proxy))

    def get_stats(self) -> ProxyStatsDataclass:
        """Get proxy statistics"""
        if not self._proxy:
            return ProxyStatsDataclass(
                running=False, active_connections=0, total_connections=0,
                websocket_active=0, bytes_received=0, bytes_sent=0, errors=0,
                ip_rotations=0,
                media_connections=0, uptime_secs=0,
                peak_active_connections=0, rotation_success=0,
            )

        stats = ProxyStats()
        self._lib.ghostwire_proxy_get_stats(self._proxy, byref(stats))

        return ProxyStatsDataclass(
            running=stats.running,
            active_connections=stats.active_connections,
            total_connections=stats.total_connections,
            websocket_active=stats.websocket_active,
            bytes_received=stats.bytes_received,
            bytes_sent=stats.bytes_sent,
            errors=stats.errors,
            ip_rotations=stats.ip_rotations,
            media_connections=stats.media_connections,
            uptime_secs=stats.uptime_secs,
            peak_active_connections=stats.peak_active_connections,
            rotation_success=stats.rotation_success,
        )

    def version(self) -> Optional[str]:
        """Get library version"""
        if not self._has_version_export:
            return None
        return self._lib.ghostwire_version().decode('utf-8')

    def features(self) -> Optional[str]:
        """Get features string"""
        if not self._has_features_export:
            return None
        return self._lib.ghostwire_features().decode('utf-8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if self._proxy:
            self._lib.ghostwire_proxy_free(self._proxy)
            self._proxy = None


# Module-level convenience functions

def version() -> Optional[str]:
    """Get library version"""
    lib_path = _find_library()
    lib = ctypes.CDLL(lib_path)
    version_fn = getattr(lib, "ghostwire_version", None)
    if version_fn is None:
        return None
    version_fn.restype = c_char_p
    return version_fn().decode('utf-8')


def features() -> Optional[str]:
    """Get library features"""
    lib_path = _find_library()
    lib = ctypes.CDLL(lib_path)
    features_fn = getattr(lib, "ghostwire_features", None)
    if features_fn is None:
        return None
    features_fn.restype = c_char_p
    return features_fn().decode('utf-8')


def feature_banner_lines():
    """Get the human-readable feature banner used by the examples."""
    return FRIENDLY_FEATURE_LINES if features() is not None else ()
