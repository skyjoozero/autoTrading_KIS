from dotenv import set_key
import os

class EnvClass:
    @staticmethod
    def getEnvValue(key):
        return os.getenv(key)

    @staticmethod
    def setEnvValue(dir, key, value):
        set_key(dir, key, value)