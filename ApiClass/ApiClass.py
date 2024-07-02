import requests, json
from datetime import datetime

class ApiClass:
    def __init__(self,  appKey, secretKey, realServer=True):
        self.appKey = appKey
        self.secretkey = secretKey
        self.accessToken = None
        self.accessTokenExpired: datetime.strptime = None

        if realServer:
            self.domain = 'https://openapi.koreainvestment.com:9443'
        else:
            self.domain = 'https://openapivts.koreainvestment.com:29443'

        if self.accessToken is None:
            self.getAccessToken()


    def getAccessToken(self):
        url = '/oauth2/Approval'
        body = {
            'grant_type': 'client_credentials',
            'appkey': self.appKey,
            'appsecret': self.secretkey,

        }
        response = self.callApi('POST', self.domain+url, body=json.dumps(body))

        if response is not None:
            self.accessToken = response['access_token']
            self.accessTokenExpired = datetime.strptime(response['acess_token_token_expired'], '%Y-%m-%d %H:%M:%S')

    def callApi(self, method, url, body: json.dumps = None, header: json.dumps = None):
        errCount = 0

        while True:
            if method == 'POST':
                response = requests.post(url, headers=header, data=body)
            elif method == 'GET':
                response = requests.get(url, headers=header, data=body)
            else:
                return None

            if response.status_code == '200':
                return json.loads(response.text)
            else:
                errCount += 1

            if errCount > 3:
                break

        #error method

    def checkResult(self):
        print(self.__dict__)