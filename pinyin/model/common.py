# -*- coding=utf8 -*-
import os
from sqlalchemy.ext.declarative import declarative_base

current_dir = os.path.dirname(os.path.abspath(__file__))
BaseModel = declarative_base()
