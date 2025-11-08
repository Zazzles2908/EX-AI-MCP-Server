#!/usr/bin/env python3
"""
Configuration Drift Detection for EX-AI MCP Server
Detects when configuration values diverge from expected state
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ConfigDriftDetector:
    """Detects configuration drift across the system"""

    STATE_FILE = Path("config") / "config_state.json"

    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self.state_file = self.config_dir / "config_state.json"
        self.current_state = self._capture_current_state()

    def _capture_current_state(self) -> Dict[str, str]:
        """Capture current configuration state"""
        state = {}

        # Environment variables (EXAI_*)
        env_vars = {k: v for k, v in os.environ.items() if k.startswith("EXAI_")}
        state["env_vars"] = self._hash_dict(env_vars)

        # Configuration files in src/config
        for config_file in self.config_dir.glob("*.py"):
            if config_file.name.startswith("__"):
                continue
            with open(config_file, "r") as f:
                content = f.read()
            state[f"config_{config_file.stem}"] = hashlib.md5(content.encode()).hexdigest()

        return state

    def _hash_dict(self, data: Dict) -> str:
        """Create hash of dictionary"""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def check_drift(self) -> Tuple[bool, List[str]]:
        """Check for configuration drift"""
        if not self.state_file.exists():
            self.save_state()
            return False, ["First configuration capture - no drift check available"]

        try:
            with open(self.state_file, "r") as f:
                saved_data = json.load(f)
            saved_state = saved_data.get("state", {})
        except Exception as e:
            return True, [f"Error reading configuration state: {e}"]

        drift_detected = False
        drift_details = []

        for key, current_hash in self.current_state.items():
            if key not in saved_state:
                drift_details.append(f"New configuration item detected: {key}")
                drift_detected = True
            elif saved_state[key] != current_hash:
                drift_details.append(f"Configuration drift detected in: {key}")
                drift_detected = True

        # Check for removed configuration
        for key in saved_state:
            if key not in self.current_state:
                drift_details.append(f"Configuration item removed: {key}")
                drift_detected = True

        return drift_detected, drift_details

    def save_state(self) -> None:
        """Save current configuration state"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        state_data = {
            "timestamp": datetime.now().isoformat(),
            "state": self.current_state,
        }

        with open(self.state_file, "w") as f:
            json.dump(state_data, f, indent=2)


def check_config_drift() -> Tuple[bool, List[str]]:
    """
    Convenience function to check for configuration drift

    Returns:
        Tuple[bool, List[str]]: (has_drift, drift_details)
    """
    detector = ConfigDriftDetector()
    return detector.check_drift()
