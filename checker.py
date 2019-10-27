#!/usr/bin/env python3

import sqlite3
from bs4 import BeautifulSoup
import requests
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QMainWindow, QMessageBox, QTableWidgetItem, QWidget, QTableWidget, QPushButton, QLineEdit, QInputDialog
from PyQt5.QtCore import QSize


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(450,500))
        self.setWindowTitle("Website Status Checker")
        self.setStyleSheet('background-color: gray')
        self.setAutoFillBackground(True)
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(50,80,330,351))
        self.tableWidget.setStyleSheet('background-color: white') 
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(2)
        self.tableWidget.show()
        self.tableWidget.setHorizontalHeaderLabels(['Website','Status','Code'])
        
        self.checkButton = QPushButton('Check Status',self)
        self.checkButton.setGeometry(QtCore.QRect(50, 440, 91, 25))
        self.checkButton.setEnabled(True)
        self.checkButton.show()
        self.checkButton.clicked.connect(self.check_websites)

        self.lineWebsite = QLineEdit()
        self.checkButton = QPushButton('Insert Website',self)
        self.checkButton.setGeometry(QtCore.QRect(145, 440, 110, 25))
        self.checkButton.setEnabled(True)
        self.checkButton.show()
        self.checkButton.clicked.connect(self.addWebsite)

        self.checkButton = QPushButton('Delete Website',self)
        self.checkButton.setGeometry(QtCore.QRect(260, 440, 110, 25))
        self.checkButton.setEnabled(True)
        self.checkButton.show()
        self.checkButton.clicked.connect(self.removeWebsite)

        self.add_sql_table()
        self.check_websites()
        self.loadTable()
    
    def removeWebsite(self):
        url, ok = QInputDialog.getText(self, 'Delete Website', 'Enter Website:')

        if ok:
            self.c.execute("DELETE from websites WHERE url = :url",
                          {'url': str(url)})
            self.loadTable()

    def addWebsite(self):
        url, ok = QInputDialog.getText(self, 'Input Website', 'Enter Website:')

        if ok:
            self.conn.execute("INSERT INTO websites VALUES (:url, :status, :code)", {
                  'url': str(url), 'status': None, 'code': None})
            self.loadTable()
        

    def add_sql_table(self):
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS websites (
                     url text,
                     status text,
                     code integer
                     )""")

    def check_websites(self):
        self.c.execute("SELECT url FROM websites")
        urls = (self.c.fetchall())
        for link in urls:
            print(link[0])
            try:
                request = requests.get(link[0], headers={'User-Agent': 'Mozilla/5.0'})
                if request.status_code == 200:
                    self.update_website(link[0], "UP", request.status_code)
                else:
                    self.update_website(link[0], "DOWN", request.status_code)
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
                print(str(e))   
        self.loadTable()

    def update_website(self, url, status, code):
        self.c.execute(
            """UPDATE websites SET status = :status ,code = :code WHERE url = :url """, {
                'url': url, 'status': status, 'code': code})

        
    def insert_new_website(self, url): 
        self.conn.execute("INSERT INTO websites VALUES (:url, :status, :code)", {
              'url': url, 'status': None, 'code': None})
        self.loadTable()

    def loadTable(self):
        content = 'SELECT * FROM websites'
        websites = self.c.execute(content)
        self.tableWidget.setRowCount(len(self.conn.execute(content).fetchall()))
        for row_index, row_data in enumerate(websites):
            print(row_data)
            for colm_index, colm_data in enumerate(row_data):
                print(colm_data)
                self.tableWidget.setItem(row_index, colm_index, QTableWidgetItem(str(colm_data)))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

