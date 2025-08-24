from __future__ import annotations
import platform
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import psutil

@dataclass
class CPUInfo:
    physical_cores: int
    logical_cores: int
    load_percent: float
    per_core_percent: List[float]
    freq_current_mhz: float | None

@dataclass
class MemoryInfo:
    total: int
    available: int
    used: int
    percent: float
    swap_total: int
    swap_used: int
    swap_percent: float

@dataclass
class DiskPartitionUsage:
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float

@dataclass
class NetworkInterface:
    name: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int

@dataclass
class ProcessInfo:
    pid: int
    name: str
    username: str | None
    cpu_percent: float
    memory_percent: float
    rss: int
    vms: int
    cmdline: List[str]

def _gather_cpu(interval: float) -> CPUInfo:
    per_core = psutil.cpu_percent(interval=interval, percpu=True)
    overall = sum(per_core) / max(1, len(per_core))
    freq = psutil.cpu_freq()
    return CPUInfo(
        physical_cores=psutil.cpu_count(logical=False) or psutil.cpu_count() or 0,
        logical_cores=psutil.cpu_count(logical=True) or 0,
        load_percent=overall,
        per_core_percent=per_core,
        freq_current_mhz=freq.current if freq else None,
    )

def _gather_memory() -> MemoryInfo:
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    return MemoryInfo(
        total=vm.total, available=vm.available, used=vm.used, percent=vm.percent,
        swap_total=sm.total, swap_used=sm.used, swap_percent=sm.percent
    )

def _gather_disks() -> List[DiskPartitionUsage]:
    items: List[DiskPartitionUsage] = []
    for p in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(p.mountpoint)
        except Exception:
            continue
        items.append(DiskPartitionUsage(
            device=p.device, mountpoint=p.mountpoint, fstype=p.fstype,
            total=u.total, used=u.used, free=u.free, percent=u.percent
        ))
    return items

def _gather_network() -> List[NetworkInterface]:
    stats = psutil.net_io_counters(pernic=True)
    out: List[NetworkInterface] = []
    for name, s in stats.items():
        out.append(NetworkInterface(
            name=name,
            bytes_sent=s.bytes_sent,
            bytes_recv=s.bytes_recv,
            packets_sent=getattr(s, "packets_sent", 0),
            packets_recv=getattr(s, "packets_recv", 0),
            errin=getattr(s, "errin", 0),
            errout=getattr(s, "errout", 0),
            dropin=getattr(s, "dropin", 0),
            dropout=getattr(s, "dropout", 0),
        ))
    return out

def _safe_proc_iter() -> List[ProcessInfo]:
    out: List[ProcessInfo] = []
    for p in psutil.process_iter(attrs=["pid", "name", "username", "memory_percent"]):
        try:
            with p.oneshot():
                cpu = p.cpu_percent(interval=None)
                memp = p.info.get("memory_percent") or 0.0
                mem = p.memory_info()
                cmd = p.cmdline()
                out.append(ProcessInfo(
                    pid=p.pid,
                    name=p.info.get("name") or "",
                    username=p.info.get("username"),
                    cpu_percent=cpu,
                    memory_percent=memp,
                    rss=mem.rss,
                    vms=mem.vms,
                    cmdline=cmd,
                ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return out

def top_processes(interval: float, count: int) -> List[ProcessInfo]:
    _ = _safe_proc_iter()
    time.sleep(interval)
    refreshed: List[ProcessInfo] = []
    for p in psutil.process_iter(attrs=["pid", "name", "username", "memory_percent"]):
        try:
            with p.oneshot():
                cpu = p.cpu_percent(interval=None)
                memp = p.info.get("memory_percent") or 0.0
                mem = p.memory_info()
                cmd = p.cmdline()
                refreshed.append(ProcessInfo(
                    pid=p.pid,
                    name=p.info.get("name") or "",
                    username=p.info.get("username"),
                    cpu_percent=cpu,
                    memory_percent=memp,
                    rss=mem.rss,
                    vms=mem.vms,
                    cmdline=cmd,
                ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    refreshed.sort(key=lambda x: (x.cpu_percent, x.memory_percent), reverse=True)
    return refreshed[:max(0, count)]

def collect(interval: float = 1.0, top_n: int = 5, include_procs: bool = True) -> Dict[str, Any]:
    return {
        "meta": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "timestamp": int(time.time()),
        },
        "cpu": asdict(_gather_cpu(interval)),
        "memory": asdict(_gather_memory()),
        "disks": [asdict(x) for x in _gather_disks()],
        "network": [asdict(x) for x in _gather_network()],
        "processes": [asdict(x) for x in top_processes(interval=0.5, count=top_n)] if include_procs else [],
    }
