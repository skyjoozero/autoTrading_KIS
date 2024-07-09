import json
import os
import pprint
import time
import requests

from datetime import datetime, timedelta
from EnvClass.EnvClass import EnvClass
from DBClass.DBClass import DBClass

class ApiClass:
    def __init__(self, envDir: str = '.env', realServer: bool = True):
        self.dbHandler = DBClass()
        self.envDir = envDir
        self.appKey = EnvClass.getEnvValue('APP_KEY')
        self.secretkey = EnvClass.getEnvValue('SECRET_KEY')
        self.accountNo = EnvClass.getEnvValue('ACCOUNT_NO')
        self.accountPrdtCd = EnvClass.getEnvValue('ACCOUNT_PRDT_CD')
        self.cashDeposit: int = 0
        self.stockDeposit: json.loads
        self.realServer: bool = realServer
        self.accessToken = EnvClass.getEnvValue('ACCESS_TOKEN')
        self.accessTokenExpired = EnvClass.getEnvValue('ACCESS_TOKEN_EXPIRED')

        if realServer:
            self.domain = 'https://openapi.koreainvestment.com:9443'
        else:
            self.domain = 'https://openapivts.koreainvestment.com:29443'

        if self.accessToken is None or datetime.strptime(self.accessTokenExpired, '%Y-%m-%d %H:%M:%S') < datetime.now():
            self.getAccessToken()

        self.initCashDeposit()
        self.initStockDeposit()

    def getAccessToken(self):
        url = '/oauth2/tokenP'
        body = {
            'grant_type': 'client_credentials',
            'appkey': self.appKey,
            'appsecret': self.secretkey,

        }

        response = self.callApi('POST', self.domain + url, body=json.dumps(body))['body']

        if response is not None:
            self.accessToken = 'Bearer ' + response['access_token']
            self.accessTokenExpired = response['access_token_token_expired']
            EnvClass.setEnvValue(self.envDir, 'ACCESS_TOKEN', self.accessToken)
            EnvClass.setEnvValue(self.envDir, 'ACCESS_TOKEN_EXPIRED', self.accessTokenExpired)

    def initCashDeposit(self):
        data = dict()
        isNextData = ''
        cashDepositUrl = '/uapi/domestic-stock/v1/trading/inquire-psbl-order'

        while True:
            cashDepositHeader = {
                'authorization': self.accessToken,
                'appkey': self.appKey,
                'appsecret': self.secretkey,
                'tr_id': 'TTTC8908R' if self.realServer else 'VTTC8908R',
                'tr_cont': isNextData,

            }

            cashDepositBody = {
                'CANO': self.accountNo,
                'ACNT_PRDT_CD': self.accountPrdtCd,
                'PDNO': '',
                'ORD_UNPR': '',
                'ORD_DVSN': '00',
                'CMA_EVLU_AMT_ICLD_YN': 'N',
                'OVRS_ICLD_YN': 'N',

            }

            response = self.callApi('GET', self.domain + cashDepositUrl, header=cashDepositHeader,
                                    body=cashDepositBody)
            data.update(response['body'])
            if response['header']['tr_cont'] in ['F', 'M']:
                isNextData = 'N'
                continue

            break

        self.cashDeposit = int(data['output']['max_buy_amt'])
        self.dbHandler.insertMongo('cashDeposit', data['output'])

    def initStockDeposit(self):
        stockDepositUrl = '/uapi/domestic-stock/v1/trading/inquire-balance'
        data = dict()
        isNextData = ''
        beforeCTX_AREA_FK100 = ''
        beforeCTX_AREA_NK100 = ''

        while True:
            stockDepositHeader = {
                'authorization': self.accessToken,
                'appkey': self.appKey,
                'appsecret': self.secretkey,
                'tr_id': 'TTTC8434R' if self.realServer else 'VTTC8434R',
                'tr_cont': isNextData,

            }

            stockDepositBody = {
                'CANO': self.accountNo,
                'ACNT_PRDT_CD': self.accountPrdtCd,
                'AFHR_FLPR_YN': 'N',
                'OFL_YN': '',
                'INQR_DVSN': '02',
                'UNPR_DVSN': '01',
                'FUND_STTL_ICLD_YN': 'Y',
                'FNCG_AMT_AUTO_RDPT_YN': 'N',
                'PRCS_DVSN': '00',
                'CTX_AREA_FK100': beforeCTX_AREA_FK100,
                'CTX_AREA_NK100': beforeCTX_AREA_NK100,

            }

            response = self.callApi('GET', self.domain + stockDepositUrl, header=stockDepositHeader,
                                    body=stockDepositBody)
            for item in response['body']['output1']:
                data[f'{item['pdno']}'] = item

            if response['header']['tr_cont'] in ['F', 'M']:
                isNextData = 'N'
                beforeCTX_AREA_FK100 = response['body']['ctx_area_fk100']
                beforeCTX_AREA_NK100 = response['body']['ctx_area_nk100']
                continue
            break

        self.dbHandler.deleteMongo('stockDeposit')
        self.dbHandler.insertMongo('stockDeposit', data)

    def getStockPeriodData(self, stockCode: str, startDate, endDate):
        stockPriceDataUrl = '/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice'
        data = list()
        startDatetime = datetime.strptime(startDate, "%Y%m%d")
        endDatetime = datetime.strptime(endDate, "%Y%m%d")

        while True:
            tempDatetime = startDatetime - timedelta(days=100)
            temp = endDatetime < tempDatetime
            stockPriceDataHeader = {
                'authorization': self.accessToken,
                'appkey': self.appKey,
                'appsecret': self.secretkey,
                'tr_id': 'FHKST03010100',

            }

            stockPriceDataBody = {
                'FID_COND_MRKT_DIV_CODE': 'J',
                'FID_INPUT_ISCD': stockCode,
                'FID_INPUT_DATE_1': tempDatetime.strftime('%Y%m%d') if temp else endDatetime.strftime('%Y%m%d'),
                'FID_INPUT_DATE_2': startDatetime.strftime('%Y%m%d'),
                'FID_PERIOD_DIV_CODE': 'D',
                'FID_ORG_ADJ_PRC': '0',

            }

            response = self.callApi('GET', self.domain + stockPriceDataUrl, header=stockPriceDataHeader,
                                    body=stockPriceDataBody)
            data.append(response['body']['output2'])

            if temp:
                startDatetime = tempDatetime - timedelta(days=1)
                time.sleep(0.5)
                continue
            break

        self.dbHandler.mySqlInsertStockData(stockCode, data)

    @staticmethod
    def callApi(method, url, header=None, body=None):
        errCount = 0

        while True:
            if method == 'POST':
                response = requests.post(url, headers=header, data=body)
            elif method == 'GET':
                response = requests.get(url, headers=header, params=body)
            else:
                return None

            if response.status_code == 200:
                return {
                    'header': response.headers,
                    'body': json.loads(response.text),
                }
            else:
                errCount += 1

            if errCount > 3:
                break

        print('api call error')

    def checkResult(self):
        print(self.__dict__)