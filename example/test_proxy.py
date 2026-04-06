#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GhostWire Python Test Example

Loads config.json, starts the SOCKS5 proxy, and monitors connections.
Telegram Desktop connects to this proxy via SOCKS5 on 127.0.0.1:1080.

Usage:
    python test_proxy.py                  # Run forever
    python test_proxy.py -t 60            # Run for 60 seconds
    python test_proxy.py -t 60 -i 30      # 60 seconds, stats every 30s
    python test_proxy.py -p 8080          # Use port 8080
    python test_proxy.py -c my_config.json  # Use custom config
"""

import sys
import io
import os
import time
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from ghostwire import (
    GhostWire,
    version,
    features,
    feature_banner_lines,
    ProxyStatsDataclass,
)


def print_banner():
    print("=" * 60)
    print("  GhostWire - Config-Driven Anti-DPI Telegram Proxy")
    print("=" * 60)
    print()
    sys.stdout.flush()


def print_stats(stats: ProxyStatsDataclass):
    print("\n" + "-" * 50)
    print("STATISTICS")
    print("-" * 50)
    print(f"  Running:             {'Yes' if stats.running else 'No'}")
    print(f"  Uptime:              {stats.uptime_secs}s")
    print(f"  Active connections:  {stats.active_connections}")
    print(f"  Peak connections:    {stats.peak_active_connections}")
    print(f"  Total connections:   {stats.total_connections}")
    print(f"  WebSocket active:    {stats.websocket_active}")
    print(f"  Bytes received:      {stats.bytes_received}")
    print(f"  Bytes sent:          {stats.bytes_sent}")
    print(f"  Errors:              {stats.errors}")
    print(f"  IP rotations:        {stats.ip_rotations}")
    print(f"  Rotation success:    {stats.rotation_success}")
    print(f"  Media connections:   {stats.media_connections}")
    print()


def get_config_port(config_path: str) -> int:
    import json
    try:
        with open(config_path, 'r') as f:
            cfg = json.load(f)
        return cfg.get("server", {}).get("port", 1080)
    except Exception:
        return 1080


def run_test(
    config_path: str,
    run_duration: int = -1,
    stats_interval: int = 30,
    port: int = 1080,
) -> int:

    print_banner()

    lib_version = version()
    lib_features = features()
    if lib_version is not None:
        print(f"Library version: {lib_version}")
    if lib_features is not None:
        print(f"Features: {lib_features}")
    print(f"Config file: {config_path}")
    if sys.platform == "win32":
        print("Build mode: Windows MSVC DLL")
    print(f"Stats interval: {stats_interval}s")
    print()
    sys.stdout.flush()

    gw = None
    try:
        # =====================================================================
        # Step 1: Start proxy
        # =====================================================================
        print(f"[1/3] Starting SOCKS5 proxy on 127.0.0.1:{port}...")
        banner_lines = feature_banner_lines()
        if banner_lines:
            print("      Anti-DPI features enabled:")
            for line in banner_lines:
                print(f"        - {line}")
            print()
        sys.stdout.flush()

        print("      Proxy started")
        print()
        sys.stdout.flush()

        # =====================================================================
        # Step 2: Monitor
        # =====================================================================
        if run_duration < 0:
            print(f"[2/3] Monitoring forever (press Ctrl+C to stop)...")
        else:
            print(f"[2/3] Monitoring for {run_duration} seconds...")
        print(f"      Configure Telegram Desktop to use SOCKS5 proxy:")
        print(f"        Server: 127.0.0.1")
        print(f"        Port:   {port}")
        print(f"        Login:  (empty)")
        print(f"        Password: (empty)")
        print()
        sys.stdout.flush()

        gw = GhostWire(config_path=config_path)
        gw.start()

        start_time = time.time()
        elapsed = 0
        iteration = 0

        while run_duration < 0 or elapsed < run_duration:
            time.sleep(stats_interval)
            elapsed = time.time() - start_time
            iteration += 1

            stats = gw.get_stats()
            sys.stdout.flush()
            print_stats(stats)
            sys.stdout.flush()

            if not gw.is_running():
                print("      Warning: Proxy stopped!")
                break

        print()

        # =====================================================================
        # Step 3: Stop
        # =====================================================================
        print("[3/3] Stopping proxy...")
        sys.stdout.flush()
        gw.stop()
        print("      Stopped")
        print()
        sys.stdout.flush()

        # =====================================================================
        # Final report
        # =====================================================================
        print("=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        if run_duration < 0:
            print(f"  Duration:  {elapsed:.1f}s (ran forever)")
        else:
            print(f"  Duration:  {elapsed:.1f}s")
        stats = gw.get_stats()
        print(f"  Total connections handled: {stats.total_connections}")
        print(f"  Errors: {stats.errors}")
        print()
        sys.stdout.flush()

        return 0

    except FileNotFoundError as e:
        print(f"\nERROR: Config file not found")
        print(f"  Message: {e}")
        print()
        print("  Make sure config.json exists")
        print()
        sys.stdout.flush()
        return 1

    except RuntimeError as e:
        print(f"\nERROR: {e}")
        print()
        sys.stdout.flush()
        return 2

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print()
        if gw:
            print("Stopping...")
            sys.stdout.flush()
            gw.stop()
            print("      Stopped")
        print()
        sys.stdout.flush()
        return 130

    except Exception as e:
        print(f"\nUNKNOWN ERROR: {type(e).__name__}: {e}")
        print()
        sys.stdout.flush()
        if gw:
            gw.stop()
        return 99


def main():
    default_config = os.path.join(os.path.dirname(__file__), "config.json")

    parser = argparse.ArgumentParser(
        description="GhostWire Test Example — Config-Driven Anti-DPI Proxy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_proxy.py              # Run forever with default config
  python test_proxy.py -t 60        # Run for 60 seconds
  python test_proxy.py -t 60 -i 30  # 60 seconds, stats every 30s
  python test_proxy.py -p 8080      # Use port 8080
  python test_proxy.py -c my.json   # Use custom config file
        """
    )

    parser.add_argument(
        "-c", "--config",
        type=str,
        default=default_config,
        metavar="FILE",
        help="Path to config.json (default: examples/config.json)"
    )

    parser.add_argument(
        "-t", "--time",
        type=int,
        default=-1,
        metavar="SEC",
        help="Test duration in seconds (default: run forever)"
    )

    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=30,
        metavar="SEC",
        help="Statistics interval in seconds (default: 30)"
    )

    parser.add_argument(
        "-p", "--port",
        type=int,
        default=None,
        metavar="PORT",
        help="Override config port (default: from config.json)"
    )

    args = parser.parse_args()

    if args.port is not None:
        port = args.port
    elif os.path.exists(args.config):
        port = get_config_port(args.config)
    else:
        port = 1080

    exit_code = run_test(
        config_path=args.config,
        run_duration=args.time,
        stats_interval=args.interval,
        port=port,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
