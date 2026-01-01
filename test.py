#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import glob
import shutil
import argparse
import subprocess
from dataclasses import dataclass
from collections import deque
from typing import Dict, List, Optional, Tuple


# -----------------------------
# Basic helpers
# -----------------------------

def which(bin_name: str) -> Optional[str]:
    return shutil.which(bin_name)

def run(cmd: List[str], timeout: float = 3.0) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", errors="replace").strip() or f"cmd failed: {cmd}")
    return p.stdout.decode("utf-8", errors="replace").strip()

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def read_int(path: str) -> int:
    return int(read_text(path))

def clear_screen():
    print("\033[2J\033[H", end="")

def fmt_w(w: Optional[float]) -> str:
    return "n/a" if w is None else f"{w:7.1f} W"

def fmt_temp(t: Optional[float]) -> str:
    return "n/a" if t is None else f"{t:5.1f} °C"

def safe_float(x: str) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


# -----------------------------
# Reading model
# -----------------------------

@dataclass
class Reading:
    label: str
    watts: Optional[float] = None     # real watts if available
    info: str = ""                   # extra info (temps, io, etc.)
    kind: str = "power"              # "power" or "meta"


class Smoother:
    def __init__(self, window: int):
        self.window = max(1, int(window))
        self.buf: Dict[str, deque] = {}

    def smooth(self, key: str, value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        if self.window == 1:
            return value
        d = self.buf.get(key)
        if d is None:
            d = deque(maxlen=self.window)
            self.buf[key] = d
        d.append(value)
        return sum(d) / len(d)


# -----------------------------
# CPU RAPL (powercap)
# -----------------------------

@dataclass
class RaplDomain:
    label: str
    energy_path: str
    max_range_uj: Optional[int]

class CpuRapl:
    def __init__(self, include_subdomains: bool = True):
        self.domains: List[RaplDomain] = self._discover(include_subdomains)
        self.prev_energy: Dict[str, int] = {}
        self.prev_t: Optional[float] = None

    def _discover(self, include_subdomains: bool) -> List[RaplDomain]:
        domains: List[RaplDomain] = []
        for base in sorted(glob.glob("/sys/class/powercap/*rapl:*")):
            bname = os.path.basename(base)
            if not include_subdomains and bname.count(":") != 1:
                continue

            energy = os.path.join(base, "energy_uj")
            if not os.path.exists(energy):
                continue

            name = bname
            name_path = os.path.join(base, "name")
            if os.path.exists(name_path):
                try:
                    name = read_text(name_path)
                except Exception:
                    pass

            max_range = None
            max_path = os.path.join(base, "max_energy_range_uj")
            if os.path.exists(max_path):
                try:
                    max_range = read_int(max_path)
                except Exception:
                    pass

            suffix = bname.split("rapl:", 1)[-1]
            label = f"CPU RAPL {name} ({suffix})"
            domains.append(RaplDomain(label=label, energy_path=energy, max_range_uj=max_range))
        return domains

    def available(self) -> bool:
        return len(self.domains) > 0

    def read(self) -> List[Reading]:
        if not self.available():
            return []

        now = time.perf_counter()
        if self.prev_t is None:
            # init baseline
            for d in self.domains:
                try:
                    self.prev_energy[d.label] = read_int(d.energy_path)
                except Exception:
                    self.prev_energy[d.label] = 0
            self.prev_t = now
            return [Reading(label="CPU RAPL", watts=None, info="warming up…")]

        dt = max(1e-6, now - self.prev_t)
        out: List[Reading] = []

        for d in self.domains:
            try:
                curr = read_int(d.energy_path)
                prev = self.prev_energy.get(d.label, curr)
                delta = curr - prev
                if delta < 0 and d.max_range_uj:
                    delta += d.max_range_uj

                watts = (delta / 1_000_000.0) / dt
                out.append(Reading(label=d.label, watts=watts))
                self.prev_energy[d.label] = curr
            except Exception as e:
                out.append(Reading(label=d.label, watts=None, info=f"read error: {e}"))

        self.prev_t = now
        return out


# -----------------------------
# GPU sources
# -----------------------------

class NvidiaSmi:
    def __init__(self):
        self.has = which("nvidia-smi") is not None

    def available(self) -> bool:
        return self.has

    def read(self) -> List[Reading]:
        if not self.available():
            return []
        try:
            out = run(["nvidia-smi", "--query-gpu=index,name,power.draw,temperature.gpu,utilization.gpu",
                       "--format=csv,noheader,nounits"], timeout=2.5)
            res: List[Reading] = []
            for line in out.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 5:
                    continue
                idx, name, pw, temp, util = parts[0], parts[1], parts[2], parts[3], parts[4]
                watts = safe_float(pw)
                info = f"temp={temp}°C util={util}%"
                res.append(Reading(label=f"GPU NVIDIA {idx} {name}", watts=watts, info=info))
            return res
        except Exception as e:
            return [Reading(label="GPU NVIDIA (nvidia-smi)", watts=None, info=str(e))]


class RocmSmi:
    """
    AMD GPU power via rocm-smi if available.
    Output formats vary between ROCm versions; this is best-effort.
    """
    def __init__(self):
        self.has = which("rocm-smi") is not None

    def available(self) -> bool:
        return self.has

    def read(self) -> List[Reading]:
        if not self.available():
            return []
        try:
            out = run(["rocm-smi", "--showpower", "--showtemp", "--showuse"], timeout=3.0)
            # Example lines often contain "Average Graphics Package Power:  45.0 W"
            res: List[Reading] = []
            # Split per GPU header: "GPU[0] :"
            blocks = re.split(r"\n(?=GPU\[\d+\])", out)
            for b in blocks:
                m_id = re.search(r"GPU\[(\d+)\]", b)
                if not m_id:
                    continue
                gid = m_id.group(1)

                m_pw = re.search(r"Average Graphics Package Power:\s*([0-9.]+)\s*W", b)
                m_t  = re.search(r"Temperature \(Sensor.*\):\s*([0-9.]+)\s*c", b, re.IGNORECASE)
                m_u  = re.search(r"GPU use:\s*([0-9.]+)\s*%", b, re.IGNORECASE)

                watts = safe_float(m_pw.group(1)) if m_pw else None
                info_parts = []
                if m_t: info_parts.append(f"temp={m_t.group(1)}°C")
                if m_u: info_parts.append(f"util={m_u.group(1)}%")
                info = " ".join(info_parts)

                res.append(Reading(label=f"GPU AMD ROCm {gid}", watts=watts, info=info))
            return res if res else [Reading(label="GPU AMD (rocm-smi)", watts=None, info="no parsable data")]
        except Exception as e:
            return [Reading(label="GPU AMD (rocm-smi)", watts=None, info=str(e))]


class HwmonPower:
    """
    Generic hwmon scan for power1_average / power1_input (µW).
    Can cover: AMD/Intel iGPU, some dGPU paths, NVMe controllers, PSUs, etc.
    """
    def __init__(self):
        self.nodes = self._discover()

    def _discover(self) -> List[Tuple[str, str]]:
        nodes: List[Tuple[str, str]] = []
        for hw in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
            name = os.path.basename(hw)
            name_path = os.path.join(hw, "name")
            if os.path.exists(name_path):
                try:
                    name = read_text(name_path)
                except Exception:
                    pass

            p_avg = os.path.join(hw, "power1_average")
            p_in  = os.path.join(hw, "power1_input")
            power_path = p_avg if os.path.exists(p_avg) else (p_in if os.path.exists(p_in) else None)
            if not power_path:
                continue

            nodes.append((f"HWMON {name} ({os.path.basename(hw)})", power_path))
        return nodes

    def available(self) -> bool:
        return len(self.nodes) > 0

    def read(self) -> List[Reading]:
        res: List[Reading] = []
        for label, path in self.nodes:
            try:
                uw = read_int(path)  # µW
                res.append(Reading(label=label, watts=uw / 1_000_000.0))
            except Exception as e:
                res.append(Reading(label=label, watts=None, info=f"read error: {e}"))
        return res


# -----------------------------
# NVMe (best-effort)
# - Real watts only if hwmon power sensors exist (handled by HwmonPower).
# - Here we also show NVMe temp / model etc. via nvme-cli if available.
# -----------------------------

class NvmeInfo:
    def __init__(self):
        self.has_nvme = which("nvme") is not None

    def available(self) -> bool:
        return os.path.isdir("/sys/class/nvme")

    def read(self) -> List[Reading]:
        res: List[Reading] = []
        nvs = sorted(glob.glob("/sys/class/nvme/nvme*"))
        for n in nvs:
            ctrl = os.path.basename(n)  # nvme0
            model = ""
            serial = ""
            try:
                model_path = os.path.join(n, "model")
                serial_path = os.path.join(n, "serial")
                if os.path.exists(model_path): model = read_text(model_path)
                if os.path.exists(serial_path): serial = read_text(serial_path)
            except Exception:
                pass

            temp = None
            if self.has_nvme:
                # nvme smart-log /dev/nvme0 typically includes temperature
                dev = f"/dev/{ctrl}"
                if os.path.exists(dev):
                    try:
                        out = run(["nvme", "smart-log", dev], timeout=2.5)
                        m = re.search(r"temperature\s*:\s*([0-9]+)\s*C", out, re.IGNORECASE)
                        if m:
                            temp = float(m.group(1))
                    except Exception:
                        pass

            info_parts = []
            if model: info_parts.append(f"model={model}")
            if serial: info_parts.append(f"sn={serial}")
            if temp is not None: info_parts.append(f"temp={temp:.0f}°C")

            # No watts here (unless hwmon provides it; that will appear in HwmonPower)
            res.append(Reading(label=f"NVMe {ctrl}", watts=None, info=" ".join(info_parts), kind="meta"))

        return res


# -----------------------------
# Disks (SATA/USB) - no real watts usually.
# Show IO + temp if possible and USB MaxPower (max, not live).
# -----------------------------

def parse_lsblk() -> List[Tuple[str, str, str]]:
    """
    Returns list of (name, type, tran) for disks.
    Requires lsblk.
    """
    if which("lsblk") is None:
        return []
    # NAME TYPE TRAN
    out = run(["lsblk", "-dn", "-o", "NAME,TYPE,TRAN"], timeout=2.5)
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            typ = parts[1]
            tran = parts[2] if len(parts) >= 3 else ""
            rows.append((name, typ, tran))
    return rows


def read_diskstats_bytes(dev: str) -> Optional[Tuple[int, int]]:
    """
    Read /sys/block/<dev>/stat to get sectors read/written.
    Fields:
      3: sectors read
      7: sectors written
    Linux sector usually 512 bytes.
    """
    path = f"/sys/block/{dev}/stat"
    if not os.path.exists(path):
        return None
    try:
        data = read_text(path).split()
        if len(data) < 8:
            return None
        sectors_read = int(data[2])
        sectors_written = int(data[6])
        return sectors_read, sectors_written
    except Exception:
        return None


def usb_maxpower_for_block(dev: str) -> Optional[str]:
    """
    Best-effort: find USB device directory and read bMaxPower (usually in mA*2 units or formatted).
    This is NOT live power; it's a descriptor / maximum.
    """
    # follow sysfs links
    base = f"/sys/block/{dev}/device"
    if not os.path.exists(base):
        return None
    try:
        real = os.path.realpath(base)
        # Walk up until we find a directory containing bMaxPower
        cur = real
        for _ in range(12):
            bmp = os.path.join(cur, "bMaxPower")
            if os.path.exists(bmp):
                val = read_text(bmp)
                # bMaxPower sometimes is "896mA" or "250"
                # Keep as-is
                return val
            nxt = os.path.dirname(cur)
            if nxt == cur:
                break
            cur = nxt
    except Exception:
        return None
    return None


def smart_temp(devnode: str) -> Optional[float]:
    """
    Best-effort temperature via smartctl (works if SMART pass-through supported).
    """
    if which("smartctl") is None:
        return None
    try:
        out = run(["smartctl", "-A", devnode], timeout=3.0)
        # Common patterns:
        #  - "Temperature_Celsius" ... last column numeric
        #  - "Current Drive Temperature:     35 C"
        m = re.search(r"Current Drive Temperature:\s*([0-9]+)\s*C", out, re.IGNORECASE)
        if m:
            return float(m.group(1))
        # ATA table
        for line in out.splitlines():
            if "Temperature_Celsius" in line or "Temperature_Internal" in line:
                parts = line.split()
                # last integer usually temp
                for tok in reversed(parts):
                    if tok.isdigit():
                        return float(tok)
        return None
    except Exception:
        return None


class DiskInfo:
    def __init__(self):
        self.has = which("lsblk") is not None
        self.prev: Dict[str, Tuple[int, int, float]] = {}  # dev -> (sr, sw, t)

    def available(self) -> bool:
        return self.has and os.path.isdir("/sys/block")

    def read(self) -> List[Reading]:
        res: List[Reading] = []
        for name, typ, tran in parse_lsblk():
            if typ != "disk":
                continue
            devnode = f"/dev/{name}"
            stats = read_diskstats_bytes(name)
            now = time.perf_counter()

            r_mb_s = w_mb_s = None
            if stats:
                sr, sw = stats
                if name in self.prev:
                    psr, psw, pt = self.prev[name]
                    dt = max(1e-6, now - pt)
                    # sectors to MB/s (512 bytes per sector)
                    r_mb_s = ((sr - psr) * 512) / (1024 * 1024) / dt
                    w_mb_s = ((sw - psw) * 512) / (1024 * 1024) / dt
                self.prev[name] = (sr, sw, now)

            temp = smart_temp(devnode)
            usb_mp = usb_maxpower_for_block(name) if tran == "usb" else None

            info_parts = []
            if tran:
                info_parts.append(f"tran={tran}")
            if temp is not None:
                info_parts.append(f"temp={temp:.0f}°C")
            if r_mb_s is not None and w_mb_s is not None:
                info_parts.append(f"io=R{r_mb_s:.1f}MB/s W{w_mb_s:.1f}MB/s")
            if usb_mp is not None:
                # descriptor / maximum, not live
                info_parts.append(f"USB MaxPower={usb_mp} (max, not live)")

            # Real watts typically unavailable for SATA/USB disks; show as meta.
            res.append(Reading(label=f"Disk {name}", watts=None, info=" ".join(info_parts), kind="meta"))
        return res


# -----------------------------
# System power (battery/IPMI)
# -----------------------------

class UpowerBattery:
    def __init__(self):
        self.has = which("upower") is not None
        self.dev = self._find() if self.has else None

    def _find(self) -> Optional[str]:
        try:
            out = run(["upower", "-e"], timeout=2.0)
            bats = [l.strip() for l in out.splitlines() if "battery" in l.lower()]
            return bats[0] if bats else None
        except Exception:
            return None

    def available(self) -> bool:
        return self.has and self.dev is not None

    def read(self) -> List[Reading]:
        if not self.available():
            return []
        try:
            info = run(["upower", "-i", self.dev], timeout=2.0)
            m = re.search(r"energy-rate:\s*([0-9.]+)\s*W", info)
            state = ""
            ms = re.search(r"state:\s*(\w+)", info)
            if ms:
                state = ms.group(1)
            if m:
                return [Reading(label=f"System battery energy-rate (state={state})", watts=float(m.group(1)))]
            return [Reading(label="System battery energy-rate", watts=None, info="not found")]
        except Exception as e:
            return [Reading(label="System battery energy-rate", watts=None, info=str(e))]


class IpmiPower:
    def __init__(self):
        self.has = which("ipmitool") is not None

    def available(self) -> bool:
        return self.has

    def read(self) -> List[Reading]:
        if not self.available():
            return []
        try:
            out = run(["ipmitool", "sdr"], timeout=3.5)
            # Best-effort: find first plausible watt reading
            for line in out.splitlines():
                if "watt" in line.lower():
                    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*Watts?", line, re.IGNORECASE)
                    if m:
                        sensor = line.split("|", 1)[0].strip()
                        return [Reading(label=f"System IPMI ({sensor})", watts=float(m.group(1)))]
            return [Reading(label="System IPMI", watts=None, info="no watt sensor found")]
        except Exception as e:
            return [Reading(label="System IPMI", watts=None, info=str(e))]


# -----------------------------
# Main
# -----------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Try-everything live power probe (Linux).")
    ap.add_argument("--interval", type=float, default=1.0, help="Update interval seconds (default 1.0).")
    ap.add_argument("--avg", type=int, default=5, help="Moving average window for watts (default 5). Use 1 to disable.")
    ap.add_argument("--no-rapl-subdomains", action="store_true",
                    help="CPU RAPL: show only top-level domains (package).")
    ap.add_argument("--debug", action="store_true", help="Show extra debug about missing tools/sources.")
    args = ap.parse_args()

    collectors = [
        CpuRapl(include_subdomains=(not args.no_rapl_subdomains)),
        NvidiaSmi(),
        RocmSmi(),
        HwmonPower(),
        NvmeInfo(),
        DiskInfo(),
        UpowerBattery(),
        IpmiPower(),
    ]

    smoother = Smoother(args.avg)

    # Preflight summary
    clear_screen()
    print("POWER PROBE (Try Everything) – Linux")
    print("Echte Watt nur, wenn Sensoren vorhanden (RAPL/GPU/hwmon/IPMI/Battery).")
    print("Für SATA/USB Disks meist keine Live-Watt → dafür Temp/IO/USB MaxPower (max, not live).")
    print("Beenden: STRG+C\n")

    print("Quellen:")
    for c in collectors:
        ok = False
        try:
            ok = c.available()
        except Exception:
            ok = False
        print(f" - {c.__class__.__name__}: {'OK' if ok else 'nicht verfügbar'}")
    print("\nStarte Live…")
    time.sleep(1.0)

    try:
        while True:
            t0 = time.time()
            ts = time.strftime("%Y-%m-%d %H:%M:%S")

            readings: List[Reading] = []
            for c in collectors:
                try:
                    if c.available():
                        readings.extend(c.read())
                except Exception as e:
                    if args.debug:
                        readings.append(Reading(label=f"{c.__class__.__name__}", watts=None, info=f"collector error: {e}"))

            # Build output
            power_lines: List[str] = []
            meta_lines: List[str] = []

            total_known = 0.0
            known_n = 0

            for r in readings:
                w_sm = smoother.smooth(r.label, r.watts)
                w_show = w_sm if w_sm is not None else r.watts

                if r.kind == "power":
                    line = f"{fmt_w(w_show)}  {r.label}"
                    if r.info:
                        line += f" | {r.info}"
                    power_lines.append(line)

                    if w_show is not None:
                        total_known += float(w_show)
                        known_n += 1
                else:
                    # meta
                    line = f"         {r.label}"
                    if r.info:
                        line += f" | {r.info}"
                    meta_lines.append(line)

            clear_screen()
            print(f"POWER PROBE – {ts}")
            print(f"Intervall: {args.interval:.2f}s | Avg: {args.avg}")
            print("-" * 100)

            if power_lines:
                print("POWER (Watt – echt, wenn Sensor vorhanden)")
                for ln in power_lines:
                    print(ln)
            else:
                print("POWER (Watt): keine Watt-Sensoren gefunden/lesbar.")

            print("-" * 100)
            if meta_lines:
                print("META (keine Live-Watt verfügbar → Infos/IO/Temps/USB MaxPower)")
                for ln in meta_lines:
                    print(ln)

            print("-" * 100)
            print(f"SUMME (nur bekannte Watt): {total_known:7.1f} W  |  known_sources={known_n}")

            # Keep interval stable
            dt = time.time() - t0
            time.sleep(max(0.0, args.interval - dt))

    except KeyboardInterrupt:
        print("\nBeendet.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
