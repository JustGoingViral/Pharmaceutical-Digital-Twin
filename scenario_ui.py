"""Minimal user-interface helpers for selecting scenario inputs."""

from dataclasses import dataclass


@dataclass
class ScenarioOptions:
    pricing: bool = True
    utilization: bool = True
    policy: bool = True


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
