"""Sozlamalar: muhit o'zgaruvchilaridan o'qiladi."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartsos.db")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
# Shahar ichida o'rtacha tezlik (km/soat) — yetib kelish vaqtini taxmin qilish uchun
AVG_SPEED_KMH = 30.0
