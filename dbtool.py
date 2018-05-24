#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import pymysql


class MySQLCommand(object):
    def __init__(self, host, port, user, passwd, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = passwd
        self.db = db

    def connectMysql(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.password,
                                        db=self.db, charset='utf8')
            self.cursor = self.conn.cursor()
        except:
            print('connect mysql error.')

    def queryMysql(self, sql):
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            print(row)

        except:
            print(sql + ' execute failed.')

    def insertMysql(self, table, column_value):
        column, value = ''
        for col,val in column_value:
            column += col + ","
            value += val + ","

        sql = "INSERT INTO " + table + "(" + column[:-1] + " )" + " VALUES(" + value[:-1] + "')"
        try:
            self.cursor.execute(sql)
        except:
            print("insert failed.")

    def updateMysqlSN(self, table, where, column_value):
        setStatement = ''
        for col, val in column_value:
            setStatement += col + " = " + val + ","

        sql = "UPDATE " + table + " SET " + setStatement[:-1] + "'" + " WHERE '" + where
        print("update sn:" + sql)

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()

    def closeMysql(self):
        self.cursor.close()
        self.conn.close()
