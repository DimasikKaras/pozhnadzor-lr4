from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    database_url: str = 'postgresql+psycopg2://postgres:postgres_secure_pass_2026@db:5432/pozhnadzor'
    jwt_secret_key: str = 'super-secret-jwt-key-for-pozhnadzor-2026-nstu'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    cors_origins: list[str] = ['*']

settings = Settings()
