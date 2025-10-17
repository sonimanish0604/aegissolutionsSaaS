# app/config.py
import os

SERVICE_NAME = os.getenv("SERVICE_NAME", "onboarding-service")
ENVIRONMENT  = os.getenv("ENVIRONMENT",  "dev")