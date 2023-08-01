import dataclasses
from typing import Optional


class Base:
    @classmethod
    def from_dict(cls, d):
        fields = set([f.name for f in dataclasses.fields(cls)])
        return cls(**{k: v for k, v in d.items() if k in fields})


@dataclasses.dataclass
class Application(Base):
    Id: str
    Name: str
    Description: Optional[str] = ""


@dataclasses.dataclass
class ConfigurationProfile(Base):
    ApplicationId: str
    Id: str
    Name: str
    Type: str


@dataclasses.dataclass
class HostedConfigurationVersion(Base):
    ApplicationId: str
    ConfigurationProfileId: str
    VersionNumber: int
    ContentType: str
    Content: str

    def get_json(self):
        return self.Content.read().decode("utf-8")


@dataclasses.dataclass
class DeploymentStrategy(Base):
    Id: str
    Name: str
    DeploymentDurationInMinutes: int
    GrowthType: str


@dataclasses.dataclass
class Environment(Base):
    ApplicationId: str
    Id: str
    Name: str
    State: str


@dataclasses.dataclass
class Deployment(Base):
    ApplicationId: str
    EnvironmentId: str
    DeploymentStrategyId: str
    ConfigurationProfileId: str
    DeploymentNumber: int
    DeploymentDurationInMinutes: int
    FinalBakeTimeInMinutes: int
    State: str
    PercentageComplete: float
