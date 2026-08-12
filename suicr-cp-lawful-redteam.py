#!/usr/bin/env python3
"""
Sovereign Lawful Red-Team Command & Cyber Range Dashboard (SUICR-CP)
Single-file production Streamlit dashboard for authorized cyber-range operations.

Scope: Defensive cyber range, lawful red-team simulation, mobile forensics,
wireless telemetry audit, and real-time threat hunting.

Author: SUICR-CP Architect
Environment: Linux (Ubuntu/Debian/CentOS), Python 3.10+
Dependencies:
    pip install streamlit asyncio aiohttp cryptography pandas numpy plotly
"""

import asyncio
import base64
import hashlib
import json
import random
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
    Prehashed,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SECURE SYSTEM STATE & ELLIPTIC CURVE LEDGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LedgerEntry:
    index: int
    timestamp: str
    event_type: str
    payload: Dict[str, Any]
    prev_hash: str
    signature: Optional[str] = None


class SecureLedger:
    """Local ECDSA (SECP256R1) signed audit log with chain-of-custody hashing."""

    def __init__(self):
        self._private_key = ec.generate_private_key(ec.SECP256R1())
        self._public_key = self._private_key.public_key()
        self.entries: List[LedgerEntry] = []
        self._lock = asyncio.Lock()

    @staticmethod
    def _canonical(payload: Dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)

    def _digest(self, entry: LedgerEntry) -> bytes:
        blob = (
            f"{entry.index}|{entry.timestamp}|{entry.event_type}|"
            f"{self._canonical(entry.payload)}|{entry.prev_hash}"
        )
        return hashlib.sha256(blob.encode("utf-8")).digest()

    def _sign(self, digest: bytes) -> str:
        signature = self._private_key.sign(digest, ec.ECDSA(Prehashed(hashes.SHA256())))
        r, s = decode_dss_signature(signature)
        return base64.b64encode(encode_dss_signature(r, s)).decode("ascii")

    def _verify(self, digest: bytes, signature_b64: str) -> bool:
        try:
            raw = base64.b64decode(signature_b64)
            self._public_key.verify(raw, digest, ec.ECDSA(Prehashed(hashes.SHA256())))
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False

    async def append(self, event_type: str, payload: Dict[str, Any]) -> LedgerEntry:
        async with self._lock:
            prev_hash = self.entries[-1].signature if self.entries else "0" * 64
            entry = LedgerEntry(
                index=len(self.entries),
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                payload=payload,
                prev_hash=prev_hash,
            )
            digest = self._digest(entry)
            entry.signature = self._sign(digest)
            self.entries.append(entry)
            return entry

    def verify_ledger(self) -> Tuple[bool, int]:
        for i, entry in enumerate(self.entries):
            digest = self._digest(entry)
            if not entry.signature or not self._verify(digest, entry.signature):
                return False, i
        return True, -1

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for e in self.entries:
            rows.append(
                {
                    "Index": e.index,
                    "Timestamp": e.timestamp,
                    "Event": e.event_type,
                    "Payload": self._canonical(e.payload)[:120] + "...",
                    "PrevHash": e.prev_hash[:16] + "...",
                    "Signature": (e.signature[:16] + "...") if e.signature else None,
                }
            )
        return pd.DataFrame(rows)

    def public_key_pem(self) -> str:
        return (
            self._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("ascii")
            .strip()
        )


class SimulationState:
    """Global thread-safe simulation state."""

    def __init__(self):
        self.lock = asyncio.Lock()
        self.ledger = SecureLedger()
        self.metrics: Dict[str, Any] = {}
        self.agents_status: Dict[str, str] = {}
        self.risk_score: float = 0.0
        self.high_risk_assets: List[str] = []
        self.last_run: Optional[str] = None

    async def update_metric(self, key: str, value: Any):
        async with self.lock:
            self.metrics[key] = value

    async def set_agent_status(self, agent: str, status: str):
        async with self.lock:
            self.agents_status[agent] = status

    async def set_risk(self, score: float, assets: List[str]):
        async with self.lock:
            self.risk_score = score
            self.high_risk_assets = assets

    async def snapshot(self) -> Dict[str, Any]:
        async with self.lock:
            return {
                "metrics": dict(self.metrics),
                "agents_status": dict(self.agents_status),
                "risk_score": self.risk_score,
                "high_risk_assets": list(self.high_risk_assets),
                "last_run": self.last_run,
            }


GLOBAL_STATE = SimulationState()


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MITRE ATT&CK MAPPING & CYBER RANGE LAB
# ═══════════════════════════════════════════════════════════════════════════════

MITRE_ATTACK_MATRIX: Dict[str, Dict[str, str]] = {
    "T1021": {"name": "Remote Services", "tactic": "Lateral Movement", "risk": "HIGH"},
    "T1190": {"name": "Exploit Public-Facing Application", "tactic": "Initial Access", "risk": "HIGH"},
    "T1133": {"name": "External Remote Services", "tactic": "Initial Access", "risk": "MEDIUM"},
    "T1110": {"name": "Brute Force", "tactic": "Credential Access", "risk": "MEDIUM"},
    "T1083": {"name": "File and Directory Discovery", "tactic": "Discovery", "risk": "LOW"},
    "T1057": {"name": "Process Discovery", "tactic": "Discovery", "risk": "LOW"},
    "T1018": {"name": "Remote System Discovery", "tactic": "Discovery", "risk": "MEDIUM"},
    "T1040": {"name": "Network Sniffing", "tactic": "Credential Access", "risk": "HIGH"},
    "T1497": {"name": "Virtualization/Sandbox Evasion", "tactic": "Defense Evasion", "risk": "MEDIUM"},
    "T1567": {"name": "Exfiltration Over Web Service", "tactic": "Exfiltration", "risk": "HIGH"},
    "T1543": {"name": "Create or Modify System Process", "tactic": "Persistence", "risk": "HIGH"},
    "T1556": {"name": "Modify Authentication Process", "tactic": "Credential Access", "risk": "HIGH"},
    "T1429": {"name": "Capture Audio", "tactic": "Collection", "risk": "CRITICAL"},
    "T1430": {"name": "Access Contact List", "tactic": "Collection", "risk": "MEDIUM"},
    "T1417": {"name": "Attack via Physical Access", "tactic": "Initial Access", "risk": "HIGH"},
    "T1428": {"name": "Broadcast Receivers", "tactic": "Collection", "risk": "MEDIUM"},
    "T1421": {"name": "Network Traffic Capture", "tactic": "Credential Access", "risk": "HIGH"},
    "T1409": {"name": "Access Stored Application Data", "tactic": "Collection", "risk": "HIGH"},
    "T1456": {"name": "Masquerade as Legitimate Application", "tactic": "Defense Evasion", "risk": "HIGH"},
    "T1465": {"name": "Impersonate SSID", "tactic": "Initial Access", "risk": "HIGH"},
}


def get_mitre_techniques_for_finding(finding_type: str, risk_level: str) -> List[str]:
    """Return relevant MITRE technique IDs based on finding category."""
    mapping = {
        "open_risk_port": ["T1021", "T1190", "T1133"],
        "compliance_failure": ["T1543", "T1556", "T1497"],
        "throughput_degradation": ["T1497", "T1040"],
        "telemetry_drift": ["T1497", "T1083"],
        "jailbreak": ["T1417", "T1456"],
        "plaintext_storage": ["T1409", "T1430"],
        "wireless_rogue_ap": ["T1465", "T1040"],
        "wireless_unencrypted": ["T1040", "T1421"],
        "wireless_ssid_spoof": ["T1465", "T1456"],
        "mobile_ioc": ["T1429", "T1428", "T1409", "T1567"],
        "geospatial_grid_abnormal": ["T1018", "T1567"],
    }
    return mapping.get(finding_type, ["T1083"])


def build_mitre_lookup_table() -> pd.DataFrame:
    rows = []
    for tid, info in MITRE_ATTACK_MATRIX.items():
        rows.append(
            {
                "Technique ID": tid,
                "Name": info["name"],
                "Tactic": info["tactic"],
                "Default Risk": info["risk"],
            }
        )
    return pd.DataFrame(rows)


class AgentA_Topology:
    """Simulated rapid subnet mapping and open-port configuration risk matching."""

    def __init__(self, state: SimulationState):
        self.state = state

    async def execute(self, subnets: List[str], vm_count: int = 8) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentA_Topology", "RUNNING")
        await self.state.ledger.append("AgentA_Topology", {"subnets": subnets, "vm_count": vm_count})

        vms = []
        findings = []
        rng = random.Random(int(time.time()))

        # Generate cyber-range lab VMs
        for i in range(vm_count):
            subnet = subnets[i % len(subnets)] if subnets else "10.0.0.0/24"
            prefix = subnet.rsplit(".", 1)[0]
            host_ip = f"{prefix}.{rng.randint(10, 250)}"
            os_type = rng.choice(["Ubuntu 22.04", "Windows Server 2022", "Debian 11", "CentOS 8"])
            role = rng.choice(["Web", "Database", "AD-DC", "FileServer", "JumpHost", "Monitoring"])
            vm = {
                "vm_id": f"vm-{i+1:03d}",
                "hostname": f"lab-{role.lower()}-{i+1}",
                "ip": host_ip,
                "subnet": subnet,
                "os": os_type,
                "role": role,
                "status": rng.choice(["ONLINE", "ONLINE", "ONLINE", "MAINTENANCE"]),
            }
            vms.append(vm)

            # Port scan simulation
            common_ports = [22, 80, 443, 3389, 21, 23, 445, 3306, 5432, 8080, 9200]
            open_ports = sorted(rng.sample(common_ports, k=rng.randint(2, 5)))
            risk_ports = [p for p in open_ports if p in [21, 23, 3389, 445, 3306, 5432, 9200]]
            risk_level = "HIGH" if risk_ports else ("MEDIUM" if any(p in [80, 8080] for p in open_ports) else "LOW")

            finding = {
                "vm_id": vm["vm_id"],
                "host": host_ip,
                "hostname": vm["hostname"],
                "open_ports": open_ports,
                "risk_ports": risk_ports,
                "risk_level": risk_level,
                "mitre_techniques": get_mitre_techniques_for_finding(
                    "open_risk_port", risk_level
                ),
            }
            findings.append(finding)
            await asyncio.sleep(0.03)

        await self.state.update_metric("topology_vms", vms)
        await self.state.update_metric("topology_findings", findings)
        await self.state.set_agent_status("AgentA_Topology", "COMPLETED")
        await self.state.ledger.append("AgentA_Topology", {"findings_count": len(findings)})
        return {"status": "completed", "vms": vms, "findings": findings}


class AgentB_Compliance:
    """Simulated configuration risk matching against security baselines."""

    BASELINES = {
        "ssh_password_auth": False,
        "firewall_enabled": True,
        "antivirus_running": True,
        "usb_storage_blocked": True,
        "patch_level": ">= 30",
        "mfa_enabled": True,
        "logging_enabled": True,
        "backup_configured": True,
    }

    def __init__(self, state: SimulationState):
        self.state = state

    async def execute(self, endpoints: List[str]) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentB_Compliance", "RUNNING")
        await self.state.ledger.append("AgentB_Compliance", {"endpoints": endpoints})

        results = []
        for ep in endpoints:
            seed = int(hashlib.sha256(ep.encode()).hexdigest(), 16)
            rng = random.Random(seed)
            checks = {}
            score = 0
            for key, expected in self.BASELINES.items():
                if key == "patch_level":
                    actual = rng.randint(1, 45)
                    passed = actual >= 30
                else:
                    actual = rng.choice([expected, not expected])
                    passed = actual == expected
                checks[key] = {"expected": str(expected), "actual": str(actual), "passed": passed}
                score += 1 if passed else 0
            compliance_pct = round(100 * score / len(self.BASELINES), 2)
            risk_level = "HIGH" if compliance_pct < 60 else ("MEDIUM" if compliance_pct < 85 else "LOW")
            results.append(
                {
                    "endpoint": ep,
                    "checks": checks,
                    "compliance_pct": compliance_pct,
                    "risk_level": risk_level,
                    "mitre_techniques": get_mitre_techniques_for_finding(
                        "compliance_failure", risk_level
                    ),
                }
            )
            await asyncio.sleep(0.02)

        await self.state.update_metric("compliance_results", results)
        await self.state.set_agent_status("AgentB_Compliance", "COMPLETED")
        await self.state.ledger.append("AgentB_Compliance", {"endpoints_checked": len(results)})
        return {"status": "completed", "results": results}


class AgentC_ThroughputBenchmarking:
    """Safe, rate-limited performance stability loops emitting latency metrics."""

    def __init__(self, state: SimulationState):
        self.state = state

    async def execute(self, target: str, duration_sec: int = 3, rate_hz: int = 10) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentC_ThroughputBenchmarking", "RUNNING")
        await self.state.ledger.append("AgentC_ThroughputBenchmarking", {"target": target, "duration": duration_sec})

        latencies = []
        dropped = 0
        start = time.monotonic()
        count = 0
        while time.monotonic() - start < duration_sec:
            t0 = time.perf_counter()
            await asyncio.sleep(1.0 / rate_hz)
            jitter = random.gauss(0, 0.005)
            latency_ms = max(0.1, 5 + jitter * 1000 + (count % 7))
            latencies.append(latency_ms)
            if latency_ms > 12:
                dropped += 1
            count += 1

        avg_latency = round(float(np.mean(latencies)), 3) if latencies else 0.0
        p99_latency = round(float(np.percentile(latencies, 99)), 3) if latencies else 0.0
        packet_loss = round(100 * dropped / len(latencies), 2) if latencies else 0.0
        throughput = len(latencies) / duration_sec if duration_sec else 0.0
        degradation = "HIGH" if packet_loss > 5 or avg_latency > 15 else "NORMAL"

        result = {
            "target": target,
            "samples": len(latencies),
            "avg_latency_ms": avg_latency,
            "p99_latency_ms": p99_latency,
            "packet_loss_pct": packet_loss,
            "throughput_ops_sec": round(throughput, 2),
            "degradation": degradation,
            "mitre_techniques": get_mitre_techniques_for_finding(
                "throughput_degradation", "HIGH" if degradation == "HIGH" else "LOW"
            ),
        }

        await self.state.update_metric("throughput_result", result)
        await self.state.set_agent_status("AgentC_ThroughputBenchmarking", "COMPLETED")
        await self.state.ledger.append("AgentC_ThroughputBenchmarking", result)
        return {"status": "completed", "result": result}


class AgentD_TelemetryValidation:
    """Compares system variables to expose telemetry sensor drifts."""

    def __init__(self, state: SimulationState):
        self.state = state

    async def execute(self, variables: List[str]) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentD_TelemetryValidation", "RUNNING")
        await self.state.ledger.append("AgentD_TelemetryValidation", {"variables": variables})

        drifts = []
        for var in variables:
            seed = int(hashlib.sha256(var.encode()).hexdigest(), 16)
            rng = random.Random(seed)
            expected = rng.uniform(20.0, 80.0)
            actual = expected + rng.gauss(0, expected * 0.08)
            delta = abs(actual - expected)
            drift_pct = round(100 * delta / expected, 2) if expected else 0.0
            status = "CRITICAL" if drift_pct > 15 else ("WARNING" if drift_pct > 5 else "OK")
            drifts.append(
                {
                    "variable": var,
                    "expected": round(expected, 3),
                    "actual": round(actual, 3),
                    "drift_pct": drift_pct,
                    "status": status,
                    "mitre_techniques": get_mitre_techniques_for_finding(
                        "telemetry_drift", status
                    ),
                }
            )
            await asyncio.sleep(0.02)

        await self.state.update_metric("telemetry_drifts", drifts)
        await self.state.set_agent_status("AgentD_TelemetryValidation", "COMPLETED")
        await self.state.ledger.append("AgentD_TelemetryValidation", {"drift_count": len(drifts)})
        return {"status": "completed", "drifts": drifts}


class AgentF_MobileMDM:
    """Localized device evaluation center verifying Jailbreak/Root, FDE, and app storage exposure."""

    def __init__(self, state: SimulationState):
        self.state = state

    async def execute(self, devices: List[str]) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentF_MobileMDM", "RUNNING")
        await self.state.ledger.append("AgentF_MobileMDM", {"devices": devices})

        evaluations = []
        for device in devices:
            seed = int(hashlib.sha256(device.encode()).hexdigest(), 16)
            rng = random.Random(seed)
            jailbroken = rng.random() < 0.25
            fde_enabled = rng.random() < 0.85
            plaintext_apps = rng.randint(0, 4) if rng.random() < 0.3 else 0

            risk = "HIGH" if jailbroken or plaintext_apps > 0 or not fde_enabled else "LOW"
            evaluations.append(
                {
                    "device": device,
                    "jailbroken": jailbroken,
                    "fde_enabled": fde_enabled,
                    "plaintext_storage_apps": plaintext_apps,
                    "risk_level": risk,
                    "mitre_techniques": get_mitre_techniques_for_finding(
                        "jailbreak" if jailbroken else "plaintext_storage", risk
                    ),
                }
            )
            await asyncio.sleep(0.04)

        await self.state.update_metric("mdm_evaluations", evaluations)
        await self.state.set_agent_status("AgentF_MobileMDM", "COMPLETED")
        await self.state.ledger.append("AgentF_MobileMDM", {"devices_evaluated": len(evaluations)})
        return {"status": "completed", "evaluations": evaluations}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MOBILE INFRASTRUCTURE FORENSICS & THREAT HUNTING PANEL
# ═══════════════════════════════════════════════════════════════════════════════

class AgentI_MobileForensics:
    """
    Simulates ingestion of a smartphone raw storage dump / system image record.
    Parses a mock partition log to isolate IoCs: signature-less surveillance
    payloads, illegal telemetry channels, persistent hidden tunnels.
    """

    IOC_SIGNATURES = {
        "surveillance_payload": ["pegasus_like_stub", "nso_trampoline", "zero_click_daemon"],
        "telemetry_channel": ["telemetry.exfil.host", "analytics.shadow.api", "covert.metrics"],
        "hidden_tunnel": ["vpn.tunnel.persistent", "reverse.proxy.sock", "enc.dns.tunnel"],
        "persistence": ["launchd.plist.backdoor", "system_server_inject", "boot.img.patch"],
    }

    def __init__(self, state: SimulationState):
        self.state = state

    def _generate_mock_partition_log(self, msisdn: str) -> List[Dict[str, Any]]:
        """Generate a deterministic mock storage dump log for the given MSISDN."""
        seed = int(hashlib.sha256(msisdn.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        partitions = ["system", "data", "cache", "recovery", "boot", "vendor"]
        log_entries = []
        for _ in range(rng.randint(40, 80)):
            part = rng.choice(partitions)
            ioc_type = rng.choices(
                population=["surveillance_payload", "telemetry_channel", "hidden_tunnel", "persistence", "benign"],
                weights=[0.08, 0.12, 0.10, 0.10, 0.60],
                k=1,
            )[0]
            if ioc_type == "benign":
                artifact = rng.choice(["com.android.settings", "libc.so", "framework.jar", "contacts.db"])
                severity = "NONE"
            else:
                artifact = rng.choice(self.IOC_SIGNATURES[ioc_type])
                severity = rng.choice(["HIGH", "CRITICAL", "HIGH"])
            log_entries.append(
                {
                    "offset": hex(rng.randint(0x1000, 0xFFFFFFFF)),
                    "partition": part,
                    "artifact": artifact,
                    "size_kb": rng.randint(4, 4096),
                    "entropy": round(rng.uniform(3.0, 7.9), 2),
                    "ioc_type": ioc_type,
                    "severity": severity,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        return log_entries

    async def execute(self, msisdn: str) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentI_MobileForensics", "RUNNING")
        await self.state.ledger.append("AgentI_MobileForensics", {"msisdn": msisdn})

        log_entries = self._generate_mock_partition_log(msisdn)
        iocs = [e for e in log_entries if e["ioc_type"] != "benign"]
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "NONE": 0}
        for e in iocs:
            severity_counts[e["severity"]] = severity_counts.get(e["severity"], 0) + 1

        # Signature-less heuristic: high entropy + small size + persistence partition
        sigless = [
            e
            for e in iocs
            if e["entropy"] > 7.0 and e["size_kb"] < 500 and e["partition"] in ["system", "boot"]
        ]

        result = {
            "msisdn": msisdn,
            "total_artifacts": len(log_entries),
            "iocs_found": len(iocs),
            "severity_counts": severity_counts,
            "signatureless_iocs": len(sigless),
            "hidden_tunnels": len([e for e in iocs if e["ioc_type"] == "hidden_tunnel"]),
            "telemetry_channels": len([e for e in iocs if e["ioc_type"] == "telemetry_channel"]),
            "risk_level": "CRITICAL"
            if severity_counts["CRITICAL"] > 0
            else ("HIGH" if severity_counts["HIGH"] > 0 else "LOW"),
            "log_entries": log_entries,
        }

        await self.state.update_metric("mobile_forensics", result)
        await self.state.set_agent_status("AgentI_MobileForensics", "COMPLETED")
        await self.state.ledger.append(
            "AgentI_MobileForensics",
            {"iocs": len(iocs), "critical": severity_counts["CRITICAL"], "risk": result["risk_level"]},
        )
        return {"status": "completed", "result": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. LOCAL SPECTRUM & WIRELESS TELEMETRY AUDIT SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════

class AgentH_WirelessAuditSimulator:
    """
    Simulates scanning nearby wireless network environments for rogue APs,
    unencrypted handshake weaknesses, and active SSID spoofing threats.
    """

    def __init__(self, state: SimulationState):
        self.state = state

    def _generate_wireless_environment(self) -> List[Dict[str, Any]]:
        """Emulated state machine loop generating safe wireless telemetry."""
        rng = random.Random(int(time.time()))
        known_ssids = {"Corp-Secure", "Lab-Guest", "Sovereign-IoT", "Range-Admin"}
        rogue_ssids = {"Corp-Secure-Free", "Lab-Guest-Guest", "Sovereign-IoT-5G", "Free-WiFi"}
        channels = list(range(1, 15)) + [36, 40, 44, 48]
        aps = []

        # Legitimate APs
        for ssid in known_ssids:
            aps.append(
                {
                    "bssid": ":".join(f"{rng.randint(0, 255):02x}" for _ in range(6)),
                    "ssid": ssid,
                    "channel": rng.choice(channels),
                    "signal_dbm": rng.randint(-75, -35),
                    "encryption": rng.choice(["WPA3-Enterprise", "WPA2-Enterprise"]),
                    "rogue": False,
                    "spoof": False,
                    "unencrypted_handshake": False,
                    "risk_level": "LOW",
                    "mitre_techniques": [],
                }
            )

        # Rogue / spoof / unencrypted APs
        for ssid in rogue_ssids:
            is_spoof = ssid.startswith(tuple(known_ssids))
            is_unencrypted = rng.random() < 0.4
            risk = "CRITICAL" if is_spoof else ("HIGH" if is_unencrypted else "MEDIUM")
            finding_type = "wireless_ssid_spoof" if is_spoof else ("wireless_unencrypted" if is_unencrypted else "wireless_rogue_ap")
            aps.append(
                {
                    "bssid": ':'.join(f"{rng.randint(0, 255):02x}" for _ in range(6)),
                    "ssid": ssid,
                    "channel": rng.choice(channels),
                    "signal_dbm": rng.randint(-80, -40),
                    "encryption": "OPEN" if is_unencrypted else "WPA2-Personal",
                    "rogue": not is_spoof,
                    "spoof": is_spoof,
                    "unencrypted_handshake": is_unencrypted,
                    "risk_level": risk,
                    "mitre_techniques": get_mitre_techniques_for_finding(finding_type, risk),
                }
            )

        return aps

    async def execute(self) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentH_WirelessAuditSimulator", "RUNNING")
        await self.state.ledger.append("AgentH_WirelessAuditSimulator", {"scan": "initiated"})

        aps = self._generate_wireless_environment()
        rogue_count = sum(1 for ap in aps if ap["rogue"])
        spoof_count = sum(1 for ap in aps if ap["spoof"])
        unencrypted_count = sum(1 for ap in aps if ap["unencrypted_handshake"])
        critical_count = sum(1 for ap in aps if ap["risk_level"] == "CRITICAL")
        high_count = sum(1 for ap in aps if ap["risk_level"] == "HIGH")

        risk_level = "CRITICAL" if critical_count else ("HIGH" if high_count else "LOW")

        result = {
            "aps_scanned": len(aps),
            "rogue_count": rogue_count,
            "spoof_count": spoof_count,
            "unencrypted_count": unencrypted_count,
            "risk_level": risk_level,
            "aps": aps,
        }

        await self.state.update_metric("wireless_audit", result)
        await self.state.set_agent_status("AgentH_WirelessAuditSimulator", "COMPLETED")
        await self.state.ledger.append(
            "AgentH_WirelessAuditSimulator",
            {"aps": len(aps), "rogue": rogue_count, "spoof": spoof_count, "risk": risk_level},
        )
        return {"status": "completed", "result": result}


# ═══════════════════════════════════════════════════════════════════════════════
# 5. SATELLITE IMAGERY & MULTI-CLOUD GEOSPATIAL INTELLIGENCE LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class AgentG_GeospatialIntelligence:
    """Abstract data integration bridge for mock geospatial + multi-cloud layers."""

    def __init__(self, state: SimulationState):
        self.state = state

    async def execute(
        self,
        coordinates: List[Tuple[float, float]],
        cloud_posture: Optional[Dict[str, Any]] = None,
        api_credentials_link: Optional[str] = None,
    ) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentG_GeospatialIntelligence", "RUNNING")
        await self.state.ledger.append(
            "AgentG_GeospatialIntelligence",
            {"coordinates": coordinates, "api_link": api_credentials_link},
        )

        cloud_posture = cloud_posture or {}
        layers = []
        for lat, lon in coordinates:
            seed = int(hashlib.sha256(f"{lat},{lon}".encode()).hexdigest(), 16)
            rng = random.Random(seed)

            imagery_status = rng.choice(["CLEAR", "CLOUD_COVER", "DEGRADED", "NO_SIGNAL"])
            grid_abnormality = rng.random() < 0.2
            thermal_anomaly = rng.random() < 0.1

            aws_score = cloud_posture.get("aws", rng.uniform(60, 100))
            azure_score = cloud_posture.get("azure", rng.uniform(60, 100))
            gcp_score = cloud_posture.get("gcp", rng.uniform(60, 100))
            avg_cloud = round((aws_score + azure_score + gcp_score) / 3, 2)

            threat_score = round(
                (30 if imagery_status in ["DEGRADED", "NO_SIGNAL"] else 0)
                + (25 if grid_abnormality else 0)
                + (20 if thermal_anomaly else 0)
                + max(0, 100 - avg_cloud),
                2,
            )
            threat_score = min(100.0, threat_score)
            risk_level = "HIGH" if threat_score > 70 else ("MEDIUM" if threat_score > 40 else "LOW")

            layers.append(
                {
                    "lat": lat,
                    "lon": lon,
                    "imagery_status": imagery_status,
                    "grid_abnormality": grid_abnormality,
                    "thermal_anomaly": thermal_anomaly,
                    "cloud_scores": {
                        "aws": round(aws_score, 2),
                        "azure": round(azure_score, 2),
                        "gcp": round(gcp_score, 2),
                    },
                    "avg_cloud_posture": avg_cloud,
                    "threat_score": threat_score,
                    "risk_level": risk_level,
                    "mitre_techniques": get_mitre_techniques_for_finding(
                        "geospatial_grid_abnormal", risk_level
                    ),
                }
            )
            await asyncio.sleep(0.05)

        await self.state.update_metric("geospatial_layers", layers)
        await self.state.set_agent_status("AgentG_GeospatialIntelligence", "COMPLETED")
        await self.state.ledger.append("AgentG_GeospatialIntelligence", {"layers": len(layers)})
        return {"status": "completed", "layers": layers}


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SOAR & TELEGRAM NOTIFICATION HOOK
# ═══════════════════════════════════════════════════════════════════════════════

class AgentE_SOAR:
    """Simulated Security Orchestration, Automation and Response isolation agent."""

    def __init__(self, state: SimulationState):
        self.state = state

    async def isolate(self, asset: str) -> Dict[str, Any]:
        await self.state.set_agent_status("AgentE_SOAR", "ISOLATING")
        await self.state.ledger.append("AgentE_SOAR", {"action": "isolate", "asset": asset})
        await asyncio.sleep(0.2)
        await self.state.set_agent_status("AgentE_SOAR", "ISOLATED")
        return {"asset": asset, "action": "isolate", "result": "success"}


async def send_telegram_alert(bot_token: str, chat_id: str, message: str) -> Dict[str, Any]:
    """Sends an encrypted HTTPS alert via Telegram Bot API."""
    if not bot_token or not chat_id:
        return {"ok": False, "error": "Missing bot_token or chat_id"}

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, ssl=True, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                data = await resp.json()
                return {"ok": data.get("ok", False), "status": resp.status, "response": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════════
# 7. AUTONOMOUS STRATEGIC COMMANDER
# ═══════════════════════════════════════════════════════════════════════════════

class AutonomousStrategicCommander:
    """
    Core orchestrator. Evaluates network, mobile forensics, wireless audit,
    telemetry, and geospatial/cloud security, triggers SOAR isolation for
    HIGH/CRITICAL assets, and dispatches Telegram alerts.
    """

    def __init__(self, state: SimulationState):
        self.state = state
        self.agent_a = AgentA_Topology(state)
        self.agent_b = AgentB_Compliance(state)
        self.agent_c = AgentC_ThroughputBenchmarking(state)
        self.agent_d = AgentD_TelemetryValidation(state)
        self.agent_f = AgentF_MobileMDM(state)
        self.agent_g = AgentG_GeospatialIntelligence(state)
        self.agent_h = AgentH_WirelessAuditSimulator(state)
        self.agent_i = AgentI_MobileForensics(state)
        self.agent_e = AgentE_SOAR(state)

    async def run(
        self,
        subnets: List[str],
        endpoints: List[str],
        devices: List[str],
        msisdn: str,
        geo_coords: List[Tuple[float, float]],
        cloud_posture: Dict[str, Any],
        bot_token: str,
        chat_id: str,
    ) -> Dict[str, Any]:
        await self.state.set_agent_status("Commander", "RUNNING")
        await self.state.ledger.append("Commander", {"phase": "init"})

        # Phase 1: Network, compliance, throughput, telemetry (parallel)
        network_task = asyncio.create_task(self.agent_a.execute(subnets))
        compliance_task = asyncio.create_task(self.agent_b.execute(endpoints))
        throughput_task = asyncio.create_task(self.agent_c.execute("lab-gateway", duration_sec=2, rate_hz=10))
        telemetry_task = asyncio.create_task(
            self.agent_d.execute(["cpu_temp", "fan_rpm", "memory_pressure", "disk_iops", "network_io"])
        )

        network, compliance, throughput, telemetry = await asyncio.gather(
            network_task, compliance_task, throughput_task, telemetry_task
        )

        # Phase 2: Mobile fleet, mobile forensics, wireless audit (parallel)
        mobile_task = asyncio.create_task(self.agent_f.execute(devices))
        forensics_task = asyncio.create_task(self.agent_i.execute(msisdn))
        wireless_task = asyncio.create_task(self.agent_h.execute())

        mobile, forensics, wireless = await asyncio.gather(mobile_task, forensics_task, wireless_task)

        # Phase 3: Geospatial / multi-cloud
        geospatial = await self.agent_g.execute(
            coordinates=geo_coords,
            cloud_posture=cloud_posture,
        )

        # Aggregate HIGH/CRITICAL risk assets
        high_risk_assets: List[str] = []

        for f in network.get("findings", []):
            if f.get("risk_level") in ("HIGH", "CRITICAL"):
                high_risk_assets.append(f"host:{f['host']}")

        for r in compliance.get("results", []):
            if r.get("risk_level") in ("HIGH", "CRITICAL"):
                high_risk_assets.append(f"endpoint:{r['endpoint']}")

        for e in mobile.get("evaluations", []):
            if e.get("risk_level") in ("HIGH", "CRITICAL"):
                high_risk_assets.append(f"device:{e['device']}")

        if forensics.get("result", {}).get("risk_level") in ("HIGH", "CRITICAL"):
            high_risk_assets.append(f"mobile-forensics:{msisdn}")

        if wireless.get("result", {}).get("risk_level") in ("HIGH", "CRITICAL"):
            high_risk_assets.append("wireless:environment")

        for layer in geospatial.get("layers", []):
            if layer.get("risk_level") == "HIGH":
                high_risk_assets.append(f"geo:{layer['lat']},{layer['lon']}")

        if throughput.get("result", {}).get("degradation") == "HIGH":
            high_risk_assets.append("throughput:lab-gateway")

        for d in telemetry.get("drifts", []):
            if d.get("status") == "CRITICAL":
                high_risk_assets.append(f"telemetry:{d['variable']}")

        # Compute overall risk score
        score = min(100.0, len(high_risk_assets) * 10.0)
        await self.state.set_risk(score, high_risk_assets)
        await self.state.ledger.append(
            "Commander",
            {"risk_score": score, "high_risk_count": len(high_risk_assets)},
        )

        # Phase 4: SOAR isolation + Telegram alert if HIGH/CRITICAL
        telegram_result = {"ok": False, "note": "No alert triggered"}
        if score >= 40 and high_risk_assets:
            for asset in high_risk_assets[:5]:
                await self.agent_e.isolate(asset)

            alert_message = (
                f"🚨 *SUICR-CP LAWFUL RED-TEAM ALERT* 🚨\n"
                f"Risk Score: `{score}`\n"
                f"Isolated Assets:\n"
                + "\n".join(f"• `{a}`" for a in high_risk_assets[:10])
                + f"\nTimestamp: `{datetime.now(timezone.utc).isoformat()}`"
            )
            telegram_result = await send_telegram_alert(bot_token, chat_id, alert_message)

        await self.state.ledger.append(
            "Commander",
            {"phase": "complete", "telegram_ok": telegram_result.get("ok")},
        )
        await self.state.set_agent_status("Commander", "COMPLETED")
        async with self.state.lock:
            self.state.last_run = datetime.now(timezone.utc).isoformat()

        return {
            "risk_score": score,
            "high_risk_assets": high_risk_assets,
            "telegram_result": telegram_result,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 8. STREAMLIT FRONTEND (MOBILE-OPTIMIZED)
# ═══════════════════════════════════════════════════════════════════════════════

def render_header():
    st.set_page_config(
        page_title="SUICR-CP Red-Team",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("🛡️ Sovereign Lawful Red-Team Command & Cyber Range")
    st.caption("Authorized cyber-range operations | MITRE ATT&CK mapped | Mobile-optimized Streamlit dashboard.")


def render_sidebar() -> Dict[str, Any]:
    st.sidebar.header("⚙️ Operator Configuration")

    bot_token = st.sidebar.text_input("Telegram Bot Token", type="password", key="bot_token")
    chat_id = st.sidebar.text_input("Telegram Chat ID", key="chat_id")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Target Lab Parameters")

    subnet_override = st.sidebar.text_input("Target Lab Subnet Override", "10.0.1.0/24")
    msisdn = st.sidebar.text_input("Simulated MSISDN Asset Parameter", "+966500000001")

    subnets = st.sidebar.text_area("Subnets (comma separated)", "10.0.1.0/24, 192.168.10.0/24, 172.16.5.0/24")
    endpoints = st.sidebar.text_area("Endpoints (comma separated)", "srv-web-01, srv-db-02, wks-finance-03")
    devices = st.sidebar.text_area("Mobile Devices (comma separated)", "iphone-sec-01, pixel-mdm-02, samsung-ops-03")
    coords_raw = st.sidebar.text_area(
        "Geospatial Coordinates (lat,lon per line)",
        "24.7136,46.6753\n25.2048,55.2708\n21.3891,39.8579",
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("☁️ Multi-Cloud Posture Scores")
    aws_score = st.sidebar.slider("AWS Posture", 0, 100, 75)
    azure_score = st.sidebar.slider("Azure Posture", 0, 100, 70)
    gcp_score = st.sidebar.slider("GCP Posture", 0, 100, 80)

    # Parse coordinates
    coordinates: List[Tuple[float, float]] = []
    for line in coords_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            lat_s, lon_s = line.split(",")
            coordinates.append((float(lat_s.strip()), float(lon_s.strip())))
        except Exception:
            st.sidebar.warning(f"Invalid coordinate line: {line}")

    return {
        "bot_token": bot_token,
        "chat_id": chat_id,
        "subnet_override": subnet_override,
        "msisdn": msisdn,
        "subnets": [s.strip() for s in subnets.split(",") if s.strip()],
        "endpoints": [e.strip() for e in endpoints.split(",") if e.strip()],
        "devices": [d.strip() for d in devices.split(",") if d.strip()],
        "coordinates": coordinates,
        "cloud_posture": {"aws": aws_score, "azure": azure_score, "gcp": gcp_score},
    }


def run_commander_sync(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run async commander safely outside Streamlit's event loop."""
    import concurrent.futures

    async def _run():
        commander = AutonomousStrategicCommander(GLOBAL_STATE)
        return await commander.run(
            subnets=config["subnets"],
            endpoints=config["endpoints"],
            devices=config["devices"],
            msisdn=config["msisdn"],
            geo_coords=config["coordinates"],
            cloud_posture=config["cloud_posture"],
            bot_token=config["bot_token"],
            chat_id=config["chat_id"],
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, _run())
        return future.result()


def render_metrics(snapshot: Dict[str, Any]):
    st.subheader("📊 Operational KPIs")
    cols = st.columns(4)
    cols[0].metric("Risk Score", snapshot.get("risk_score", 0), delta=None)
    cols[1].metric("High-Risk Assets", len(snapshot.get("high_risk_assets", [])))
    cols[2].metric("Agents Active", len(snapshot.get("agents_status", {})))
    cols[3].metric("Last Run", snapshot.get("last_run", "—")[:19] if snapshot.get("last_run") else "—")


def render_command_center(config: Dict[str, Any]):
    st.markdown("---")
    st.subheader("🚀 Autonomous Strategic Commander Matrix")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        fire = st.button("🔥 FIRE COMMANDER", use_container_width=True)
    with col2:
        verify = st.button("🔍 VERIFY LEDGER", use_container_width=True)

    if fire:
        with st.spinner("Executing lawful red-team strategic cycle..."):
            result = run_commander_sync(config)
        st.success(f"Commander cycle complete. Risk Score: {result['risk_score']}")
        if result.get("high_risk_assets"):
            st.warning(f"High-risk assets: {', '.join(result['high_risk_assets'][:10])}")
        st.json(result.get("telegram_result", {}))

    if verify:
        valid, tampered_index = GLOBAL_STATE.ledger.verify_ledger()
        if valid:
            st.success("Ledger integrity verified.")
        else:
            st.error(f"Tamper detected at index {tampered_index}.")


def expand_mitre_details(df: pd.DataFrame) -> pd.DataFrame:
    """Add MITRE tactic/name/risk columns to a findings dataframe."""
    if df.empty or "mitre_techniques" not in df.columns:
        return df
    df["MITRE Details"] = df["mitre_techniques"].apply(
        lambda tids: ", ".join(
            f"{tid}: {MITRE_ATTACK_MATRIX.get(tid, {}).get('name', 'Unknown')}" for tid in tids
        )
    )
    return df


def render_status_tabs(snapshot: Dict[str, Any]):
    tabs = st.tabs(
        [
            "Agent Status",
            "Cyber Range",
            "MITRE Matrix",
            "Compliance",
            "Throughput",
            "Telemetry",
            "MDM",
            "Mobile Forensics",
            "Wireless Audit",
            "Geospatial",
            "Ledger",
        ]
    )
    agents = snapshot.get("agents_status", {})
    metrics = snapshot.get("metrics", {})

    with tabs[0]:
        df_status = pd.DataFrame([{"Agent": k, "Status": v} for k, v in agents.items()])
        st.dataframe(df_status, use_container_width=True)

    with tabs[1]:
        vms = metrics.get("topology_vms", [])
        findings = metrics.get("topology_findings", [])
        st.markdown("**Virtual Machines**")
        st.dataframe(pd.DataFrame(vms), use_container_width=True)
        st.markdown("**Vulnerability Findings**")
        df_findings = expand_mitre_details(pd.DataFrame(findings))
        st.dataframe(df_findings, use_container_width=True)

    with tabs[2]:
        st.markdown("**Persistent MITRE ATT&CK Lookup Matrix**")
        st.dataframe(build_mitre_lookup_table(), use_container_width=True)
        st.markdown("**Active Technique Coverage**")
        all_techniques = set()
        for f in metrics.get("topology_findings", []):
            all_techniques.update(f.get("mitre_techniques", []))
        for r in metrics.get("compliance_results", []):
            all_techniques.update(r.get("mitre_techniques", []))
        for d in metrics.get("telemetry_drifts", []):
            all_techniques.update(d.get("mitre_techniques", []))
        for e in metrics.get("mdm_evaluations", []):
            all_techniques.update(e.get("mitre_techniques", []))
        for ap in metrics.get("wireless_audit", {}).get("aps", []):
            all_techniques.update(ap.get("mitre_techniques", []))
        for layer in metrics.get("geospatial_layers", []):
            all_techniques.update(layer.get("mitre_techniques", []))
        if all_techniques:
            coverage_df = pd.DataFrame(
                [
                    {
                        "Technique ID": tid,
                        "Name": MITRE_ATTACK_MATRIX.get(tid, {}).get("name", "Unknown"),
                        "Tactic": MITRE_ATTACK_MATRIX.get(tid, {}).get("tactic", "Unknown"),
                    }
                    for tid in sorted(all_techniques)
                ]
            )
            st.dataframe(coverage_df, use_container_width=True)
        else:
            st.info("Run the Commander to populate technique coverage.")

    with tabs[3]:
        results = metrics.get("compliance_results", [])
        if results:
            rows = []
            for r in results:
                rows.append(
                    {
                        "Endpoint": r["endpoint"],
                        "Compliance %": r["compliance_pct"],
                        "Risk Level": r["risk_level"],
                        "MITRE": ", ".join(r.get("mitre_techniques", [])),
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.info("No compliance data yet.")

    with tabs[4]:
        result = metrics.get("throughput_result", {})
        if result:
            st.json(result)
        else:
            st.info("No throughput data yet.")

    with tabs[5]:
        drifts = metrics.get("telemetry_drifts", [])
        if drifts:
            df = pd.DataFrame(drifts)
            st.dataframe(expand_mitre_details(df), use_container_width=True)
            fig = px.bar(df, x="variable", y="drift_pct", color="status", title="Telemetry Drift %")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No telemetry data yet.")

    with tabs[6]:
        evaluations = metrics.get("mdm_evaluations", [])
        if evaluations:
            df = pd.DataFrame(evaluations)
            st.dataframe(expand_mitre_details(df), use_container_width=True)
        else:
            st.info("No MDM data yet.")

    with tabs[7]:
        forensics = metrics.get("mobile_forensics", {})
        if forensics:
            st.markdown(f"**MSISDN:** `{forensics.get('msisdn')}`")
            st.markdown(f"**Total Artifacts:** {forensics.get('total_artifacts')}")
            st.markdown(f"**IoCs Found:** {forensics.get('iocs_found')}")
            st.markdown(f"**Signature-less IoCs:** {forensics.get('signatureless_iocs')}")
            st.markdown(f"**Hidden Tunnels:** {forensics.get('hidden_tunnels')}")
            st.markdown(f"**Telemetry Channels:** {forensics.get('telemetry_channels')}")
            st.markdown(f"**Risk Level:** {forensics.get('risk_level')}")
            st.bar_chart(
                pd.Series(forensics.get("severity_counts", {}), name="Severity Counts")
            )
            log_entries = forensics.get("log_entries", [])
            if log_entries:
                df_logs = pd.DataFrame(log_entries)
                st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("No mobile forensics data yet. Run the Commander.")

            with tabs[8]:
        wireless = metrics.get("wireless_audit", {})
        if wireless:
            st.markdown(f"**APs Scanned:** {wireless.get('aps_scanned')}")
            st.markdown(f"**Rogue APs:** {wireless.get('rogue_count')}")
            st.markdown(f"**SSID Spoofs:** {wireless.get('spoof_count')}")
            st.markdown(f"**Unencrypted Handshakes:** {wireless.get('unencrypted_count')}")
            st.markdown(f"**Wireless Risk:** {wireless.get('risk_level')}")

            aps = wireless.get("aps", [])
            if aps:
                df = pd.DataFrame(aps)
                st.dataframe(expand_mitre_details(df), use_container_width=True)
                fig = px.scatter(
                    df,
                    x="channel",
                    y="signal_dbm",
                    color="risk_level",
                    size=[10 if r in ("HIGH", "CRITICAL") else 6 for r in df["risk_level"]],
                    hover_data=["ssid", "bssid", "encryption"],
                    title="Wireless Environment Scan",
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No wireless audit data yet.")

    with tabs[9]:
        layers = metrics.get("geospatial_layers", [])
        if layers:
            df = pd.DataFrame(layers)
            st.dataframe(expand_mitre_details(df), use_container_width=True)
            fig = px.scatter_geo(
                df,
                lat="lat",
                lon="lon",
                color="risk_level",
                size="threat_score",
                hover_name="imagery_status",
                projection="natural earth",
                title="Geospatial Threat Layer",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No geospatial data yet.")

    with tabs[10]:
        ledger_df = GLOBAL_STATE.ledger.to_dataframe()
        st.dataframe(ledger_df, use_container_width=True)
        valid, tampered_index = GLOBAL_STATE.ledger.verify_ledger()
        if valid:
            st.success("Ledger integrity verified: no tampering detected.")
        else:
            st.error(f"Ledger tampering detected at index {tampered_index}.")


def main():
    render_header()
    config = render_sidebar()
    snapshot = asyncio.run(GLOBAL_STATE.snapshot())
    render_metrics(snapshot)
    render_command_center(config)
    snapshot = asyncio.run(GLOBAL_STATE.snapshot())
    render_status_tabs(snapshot)


if __name__ == "__main__":
    main()