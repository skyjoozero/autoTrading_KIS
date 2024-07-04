import json
import os
import requests
from datetime import datetime
from EnvClass.EnvClass import EnvClass


class ApiClass:
    def __init__(self, envDir: str = '.env', realServer: bool = True):

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

    def initCashDeposit(self):
        cashDepositUrl = '/uapi/domestic-stock/v1/trading/inquire-psbl-order'
        cashDepositHeader = {
            'authorization': self.accessToken,
            'appkey': self.appKey,
            'appsecret': self.secretkey,
            'tr_id': 'TTTC8908R' if self.realServer else 'VTTC8908R',

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

        self.cashDeposit = int(response['output']['max_buy_amt'])

    def getAccessToken(self):
        url = '/oauth2/tokenP'
        body = {
            'grant_type': 'client_credentials',
            'appkey': self.appKey,
            'appsecret': self.secretkey,

        }
        response = self.callApi('POST', self.domain + url, body=json.dumps(body))
        if response is not None:
            self.accessToken = 'Bearer ' + response['access_token']
            self.accessTokenExpired = response['access_token_token_expired']
            EnvClass.setEnvValue(self.envDir, 'ACCESS_TOKEN', self.accessToken)
            EnvClass.setEnvValue(self.envDir, 'ACCESS_TOKEN_EXPIRED', self.accessTokenExpired)

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

            # print(response.text)

            if response.status_code == 200:
                return json.loads(response.text)
            else:
                errCount += 1

            if errCount > 3:
                break

        # error method

        print('api call error')

    def checkResult(self):
        print(self.__dict__)
