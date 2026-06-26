from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Config:
    base_dir: str
    username: str
    password: str
    user_investment_account_id: str
    db_path: Path


def build_config() -> Config:
    base_dir = Path(__file__).resolve().parent
    return Config(
        base_dir=base_dir,
        username=get_env("MPP_USERNAME"),
        password=get_env("MPP_PASSWORD"),
        user_investment_account_id=get_env("MPP_USER_INVESTMENT_ACCOUNT_ID"),
        db_path=Path(get_env("DB_PATH"))
    )


def get_env(
    name: str
) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    elif value.upper() == "CHANGE_ME":
        raise RuntimeError(f"Environment variable is not set ({name})")
    return value
