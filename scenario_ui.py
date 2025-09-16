"""Simple UI toggles for simulation scenario inputs."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ScenarioToggle:
    """Container tracking enabled scenario inputs."""

"""Minimal user-interface helpers for selecting scenario inputs."""

from dataclasses import dataclass


@dataclass
class ScenarioOptions:
    pricing: bool = True
    utilization: bool = True
    policy: bool = True

    def toggle(self, key: str) -> None:
        if hasattr(self, key):
            setattr(self, key, not getattr(self, key))
        else:
            raise KeyError(f"Unknown scenario input: {key}")

    def as_dict(self) -> Dict[str, bool]:
        return {"pricing": self.pricing, "utilization": self.utilization, "policy": self.policy}


def interactive_toggle(toggle: ScenarioToggle) -> ScenarioToggle:
    """CLI helper to allow users to toggle inputs."""

    print("Toggle scenario inputs (pricing, utilization, policy). Enter to finish.")
    while True:
        key = input("Input to toggle (or press enter to finish): ").strip().lower()
        if not key:
            break
        try:
            toggle.toggle(key)
            print(f"{key} set to {getattr(toggle, key)}")
        except KeyError as exc:
            print(exc)
    return toggle


class ScenarioToggle:
    """Container that allows toggling simulation scenario inputs."""

    def __init__(self) -> None:
        self.options = ScenarioOptions()

    def set_option(self, name: str, value: bool) -> None:
        if not hasattr(self.options, name):
            raise ValueError(f"Unknown scenario option: {name}")
        setattr(self.options, name, value)

    def as_dict(self) -> dict:
        return self.options.__dict__.copy()
