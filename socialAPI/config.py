from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    class Config:
        env_file: str = ".env"
        extra = "allow"


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    LOGTAIL_API_KEY: Optional[str] = None


class DevConfig(BaseConfig):
    DATABASE_URL: str = "sqlite:///dev.db"
    DB_FORCE_ROLL_BACK: bool = True

    model_config = {"env_prefix": "DEV_"}

class ProdConfig(BaseConfig):
    model_config = {"env_prefix": "PROD_"}



class TestConfig(BaseConfig):
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True

    model_config = {"env_prefix": "TEST_"}



@lru_cache
def get_config(env_state: str):
    configs = {
        "dev": DevConfig,
        "test": TestConfig,
        "prod": ProdConfig,
    }

    if env_state not in configs:
        raise ValueError(f"Invalid ENV_STATE: {env_state}")
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
