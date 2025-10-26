from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    REDIS_URL = os.getenv("REDIS_URL")
    # SUPABASE_URL = os.getenv("SUPABASE_URL")
    # SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


settings = Settings()
