from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
from dotenv import load_dotenv


URL_DATABASE = "mysql://root:ppGoWIfXdrCfLiXtTTLwCJHeBldWDZOY@junction.proxy.rlwy.net:49390/railway"

engine = create_engine(URL_DATABASE)

sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()