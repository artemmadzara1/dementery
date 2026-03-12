import os



class Config:
      APP_NAME = "Dementery"
      SECRET_KEY =os.environ.get('SECRET_KEY', os.urandom(24))
      DEBUG = True
