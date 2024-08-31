from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SQLDB_URL: str
    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5 * 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60

    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env", validate_assignment = True, extra = "allow")
    
def get_setting():
    return Settings()