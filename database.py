from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
from dotenv import load_dotenv


load_dotenv()


URL_DATABASE = os.getenv("URL_REMOTE_DATABASE")

engine = create_engine(URL_DATABASE)

sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()