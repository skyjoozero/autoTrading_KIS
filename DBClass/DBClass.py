import pymysql

from pymongo import MongoClient
from EnvClass.EnvClass import EnvClass

class DBClass:
    def __init__(self):
        self.dbUserName = EnvClass.getEnvValue('DB_USERNAME')
        self.dbPassword = EnvClass.getEnvValue('DB_PASSWORD')
        self.dbIpAddr = EnvClass.getEnvValue('DB_IP_ADDR')
        self.mongoDbPortNum = EnvClass.getEnvValue('MONGO_DB_PORT_NUM')
        self.mySqlDbPortNum = EnvClass.getEnvValue('MYSQL_DB_PORT_NUM')
        self.mySqlDbName = 'autoTrading_' + self.dbUserName

        self.mongoDbClient = MongoClient('mongodb://' + self.dbUserName + ':' +
                                         self.dbPassword + '@' + self.dbIpAddr +
                                         ':' + self.mongoDbPortNum + '/')
        self.mongoDbCollectionHandler = self.mongoDbClient['autoTrading'][self.dbUserName]
        self.mySqlConn = pymysql.connect(host=self.dbIpAddr, port=int(self.mySqlDbPortNum), user=self.dbUserName, password=self.dbPassword, charset='utf8')
        self.mySqlCur = self.mySqlConn.cursor();

        self.mySqlCur.execute(f'CREATE DATABASE IF NOT EXISTS {self.mySqlDbName};')
        self.mySqlCur.execute('use autoTrading_' + self.dbUserName)

    def insertMongo(self, idStr, data):
        if len(data) == 0:
            return None
        if isinstance(data, list):
            data = {'_id': idStr,
                    'data': data}
            if self.checkMongoDocExist(idStr):
                data = {'$set': data}
                self.mongoDbCollectionHandler.update_many({'_id': idStr}, data)
            else:
                self.mongoDbCollectionHandler.insert_many(data)
        else:
            data['_id'] = idStr
            if self.checkMongoDocExist(idStr):
                data = {'$set': data}
                self.mongoDbCollectionHandler.update_one({'_id': idStr}, data)
            else:
                self.mongoDbCollectionHandler.insert_one(data)


    def checkMongoDocExist(self, idStr: str):
        return self.mongoDbCollectionHandler.count_documents({'_id': idStr}) > 0

    def checkMySqlTableExist(self, tableStr: str):
        self.mySqlCur.execute(f'SHOW TABLES FROM {self.mySqlDbName} LIKE "{tableStr}";')
        return len(self.mySqlCur.fetchall()) > 0

    def test(self):
        data = {
            'ad': 'df',
            'name': 'jooyoung',

        }
        postId = self.posts.insert_one(data).inserted_id
        print(postId)
