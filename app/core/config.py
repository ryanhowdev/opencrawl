from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Configuration settings for the application.
    This will automatically read from environment variables.
    """

    # Database connection URL
    DATABASE_URL: str = "postgresql://user:password@localhost/mydatabase"
    
    # Redis broker for Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Secret key for OAuth2 token handling
    SECRET_KEY: str = "supersecretkey"
    
    # Token expiration time (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"  # Load environment variables from a .env file

# Instantiate the settings
settings = Settings()
