import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
EVIDENCE_DIR = DATA_DIR / "evidence"
REPORTS_DIR = DATA_DIR / "reports"

DATA_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous AI QA Testing Agent"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'qa_agent.db'}"
    
    # LLM Settings
    LLM_PROVIDER: str = "heuristic"  # 'openai', 'ollama', 'heuristic'
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    
    # Browser Automation Settings
    DEFAULT_BROWSER: str = "chromium"  # 'chromium', 'firefox', 'webkit'
    HEADLESS: bool = True
    BROWSER_TIMEOUT_MS: int = 30000
    ACTION_TIMEOUT_MS: int = 10000
    PAGE_LOAD_TIMEOUT_MS: int = 30000
    
    # Agent State Machine & Safety
    MAX_RETRIES: int = 2
    MAX_AGENT_STEPS: int = 100
    CONFIDENCE_THRESHOLD: float = 0.70
    
    # Directories
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    EVIDENCE_DIR: Path = EVIDENCE_DIR
    REPORTS_DIR: Path = REPORTS_DIR
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
