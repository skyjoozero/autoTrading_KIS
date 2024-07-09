from ApiClass.ApiClass import ApiClass
import dotenv, os
from DBClass import DBClass

if __name__ == '__main__':
    dotenv.load_dotenv()

    # dbClass = DBClass.DBClass()
    apiClass = ApiClass('.env', realServer=True)
    # apiClass.getStockPeriodData('338220', '20240709', '20220101')
    # apiClass.checkResult()