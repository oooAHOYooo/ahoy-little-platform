import sys
import os
sys.path.append(os.getcwd())
from app import create_app
from db import get_session
from models import Base, AnalyticsEvent
from sqlalchemy import create_engine
from config import get_config

app = create_app()
with app.app_context():
    config = get_config()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    if not engine.dialect.has_table(engine.connect(), "analytics_events"):
        print("Creating analytics_events table...")
        AnalyticsEvent.__table__.create(engine)
        print("Done.")
    else:
        print("Table analytics_events already exists.")
