import os

class Config:
    #Clave secreta para la gestión de sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'N^nD@gtwQ4r*88pxHF6#kn*tDCaZn3PPc3$^hGyBF3bCDGh8$ZtrnevKFycuU4%J'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False