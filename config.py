import os
from dotenv import load_dotenv

load_dotenv()
class Config:
     SECRET_KEY =os.getenv('SECRET_KEY',"dementery321")
     DATABASE ='dementery.db'
     DEBUG = os.getenv('DEBUG',"True") == "True"
