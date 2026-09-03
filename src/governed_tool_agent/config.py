"""Application configuration kept deliberately small for the Day 1 runtime."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    environment: str = "development"
    policy_version: str = "day1"

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            environment=os.getenv("GOVERNED_AGENT_ENV", "development"),
            policy_version=os.getenv("GOVERNED_AGENT_POLICY_VERSION", "day1"),
        )
