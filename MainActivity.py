from ApiClass.ApiClass import ApiClass
import dotenv, os

if __name__ == '__main__':
    dotenv.load_dotenv()

    apiClass = ApiClass(os.getenv('APP_KEY'), os.getenv('SECRET_KEY'))

    apiClass.check