import configparser
import os


config = configparser.ConfigParser()
config.read('./config/config.ini')


def getDatasetPath():
    homepath = os.getenv("HOME_PATH")
    print(homepath)
    path = homepath+ config["DEFAULT"]["dataset"]
    return path

def getDatabaseDir():
    homepath = os.getenv("HOME_PATH")
    path = homepath+ config["DEFAULT"]["databaseDir"]
    return path

def getProperty(propertyName):
    return config["DEFAULT"][propertyName]