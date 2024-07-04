import pymysql

from pymongo import MongoClient
from EnvClass.EnvClass import EnvClass

class DBClass:
    def __init__(self):
        self.dbUserName = EnvClass.getEnvValue('DB_USERNAME')
        self.dbPassword = EnvClass.getEnvValue('DB_PASSWORD')
        self.dbIpAddr = EnvClass.getEnvValue('DB_IP_ADDR')
        self.MongoDbPortNum = EnvClass.getEnvValue('MONGO_DB_PORT_NUM')
        self.mySqlDbPortNum = EnvClass.getEnvValue('MYSQL_DB_PORT_NUM')

        self.MongoDbClient = MongoClient('mongodb://' + self.dbUserName + ':' +
                                         self.dbPassword + '@' + self.dbIpAddr +
                                         ':' + self.MongoDbPortNum + '/')
        self.mySqlConn = pymysql.connect(host=self.dbIpAddr, port=int(self.mySqlDbPortNum), user=self.dbUserName, password=self.dbPassword, charset='utf8')
        self.mySqlCur = self.mySqlConn.cursor();



    def test(self):
        data = {
            'ad': 'df',
            'name': 'jooyoung',

        }
        postId = self.posts.insert_one(data).inserted_id
        print(postId)
