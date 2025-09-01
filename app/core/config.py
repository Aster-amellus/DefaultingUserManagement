from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Contract Default Management API"
    database_url: str = "sqlite+pysqlite:///./dev.db"

    jwt_secret_key: str = "devsecret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    admin_default_email: str = "admin@example.com"
    admin_default_password: str = "admin123"

    # Storage config
    storage_backend: str = "local"  # local | s3
    local_storage_dir: str = "./uploads"
    public_base_url: str | None = None  # for s3 CDN or reverse proxy base
    s3_endpoint: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str | None = None
    s3_bucket: str | None = None

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False


settings = Settings()
