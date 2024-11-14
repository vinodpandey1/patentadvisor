import configparser
import os
config = configparser.ConfigParser()
config.read('./config/config.ini')


def getDatasetPath():
    homepath = os.getenv("HOME_PATH")
    print(homepath)
    path = homepath+ config["DEFAULT"]["dataset"]
    return path