from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Config:
    base_dir: Path
    user_investment_account_id: str
    db_path: Path
    report_path: Path
    capital_trends_down_sample_ratio: int
    product_trends_cutoff_date: str
    product_trends_down_sample_max_points: int


def build_config() -> Config:
    base_dir = Path(__file__).resolve().parent
    return Config(
        base_dir=base_dir,
        user_investment_account_id=get_env("MPP_USER_INVESTMENT_ACCOUNT_ID"),
        db_path=Path(get_env("DB_PATH")),
        report_path=Path(get_env("REPORT_PATH")),
        capital_trends_down_sample_ratio=int(get_env("CAPITAL_TRENDS_DOWN_SAMPLE_RATIO")),
        product_trends_cutoff_date=get_env("PRODUCT_TRENDS_CUTOFF_DATE"),
        product_trends_down_sample_max_points=int(get_env("PRODUCT_TRENDS_DOWN_SAMPLE_MAX_POINTS"))
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
