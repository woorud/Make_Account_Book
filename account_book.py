from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtCore import *
from datetime import datetime, timedelta
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import font_manager, rc

import sys
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

form_class = loadUiType("account_bookd.ui")[0]
class Home(QDialog, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("Account Book For Me")
        self.setWindowIcon(QIcon("icon.png"))

        plt.rcParams["axes.unicode_minus"] = False
        font_path = 'C:/Users/82102/AppData/Local/Microsoft/Windows/Fonts/NanumGothicCoding.ttf'
        font_name = font_manager.FontProperties(fname=font_path).get_name()
        rc("font", family=font_name)

        # DB connect
        self.dbConn = pymysql.connect(user="your_mysql_id",
                                      passwd="your_mysql_pwd",
                                      host="127.0.0.1",
                                      db="account",
                                      charset="UTF8")

        self.main()
        self.details()
        self.report()

        # Main
    def main(self):
        self.date_label.setText(QDate.currentDate().toString(Qt.DefaultLocaleLongDate))

        sql = "select list, sum(use_cost) from account_book where use_type = '수입' group by list"
        df_descimport = pd.read_sql(sql, self.dbConn)
        self.desc_import.setColumnCount(len(df_descimport.columns))
        self.desc_import.setRowCount(len(df_descimport.index))
        Row = 0
        for i in range(len(df_descimport.index)):
            x = df_descimport.iloc[i, 0]
            y = df_descimport.iloc[i, 1]
            self.desc_import.setItem(i, 0, QTableWidgetItem(x))
            self.desc_import.setItem(i, 1, QTableWidgetItem(str(int(y))+" 원"))
            self.desc_import.item(Row, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.desc_import.item(Row, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
            Row += 1

        sql = "select list, sum(use_cost) from account_book where use_type = '지출' group by list"
        df_descexport = pd.read_sql(sql, self.dbConn)
        self.desc_export.setColumnCount(len(df_descexport.columns))
        self.desc_export.setRowCount(len(df_descexport.index))
        Row = 0
        for i in range(len(df_descexport.index)):
            x = df_descexport.iloc[i, 0]
            y = df_descexport.iloc[i, 1]
            self.desc_export.setItem(i, 0, QTableWidgetItem(x))
            self.desc_export.setItem(i, 1, QTableWidgetItem(str(int(y)) + " 원"))
            self.desc_export.item(Row, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.desc_export.item(Row, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
            Row += 1

        sql = "select sum(use_cost) from account_book where use_date = '{}' and use_type = '수입'".format(QDate.currentDate().toString("yyyy-MM-dd"))
        cur = self.dbConn.cursor()
        cur.execute(sql)
        im = 0
        for i in cur:
            if i[0] != None:
                im = i[0]
        self.today_import.setText("{} 원".format("{:,}".format(im)))

        sql = "select sum(use_cost) from account_book where use_date = '{}' and use_type = '지출'".format(QDate.currentDate().toString("yyyy-MM-dd"))
        cur = self.dbConn.cursor()
        cur.execute(sql)
        ex = 0
        for i in cur:
            if i[0] != None:
                ex = i[0]
        self.today_export.setText("{} 원".format("{:,}".format(ex)))

        sql = "select sum(use_cost) from account_book where use_date = '{}'".format(QDate.currentDate().toString("yyyy-MM-dd"))
        cur = self.dbConn.cursor()
        cur.execute(sql)
        tot = im - ex
        self.today_total.setText("{} 원".format("{:,}".format(tot)))

        sql = "select use_type, sum(use_cost) as cost from account_book where type = '현금/체크카드' and use_date like '{}%' group by use_type".format(QDate.currentDate().toString("yyyy-MM"))
        df_check = pd.read_sql(sql, self.dbConn, index_col="use_type")
        if "수입" not in df_check.index:
            df_check.loc["수입"] = [0]
        elif "지출" not in df_check.index:
            df_check.loc["지출"] = [0]
        df_check = df_check.sort_index()
        y = df_check.values.flatten()
        x = df_check.index.tolist()
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.cur_chk.addWidget(self.canvas)
        ax = self.fig.add_subplot(111)
        ax.bar(x, y, color=list(mcolors.TABLEAU_COLORS.values())[:len(x)])
        ax.yaxis.set_visible(False)
        for p in ax.patches:
            left, bottom, width, height = p.get_bbox().bounds
            ax.annotate("{} 원".format("{:,}".format(int(height))), (left + width / 2, height * 1.01), ha='center')
        ax.set_title("Monthly spending status")
        self.canvas.draw()

        sql = "select use_type, sum(use_cost) as cost from account_book where type = '신용카드' and use_date like '{}%' group by use_type".format(QDate.currentDate().toString("yyyy-MM"))
        df_credit = pd.read_sql(sql, self.dbConn, index_col="use_type")
        if "수입" not in df_credit.index:
            df_credit.loc["수입"] = [0]
        elif "지출" not in df_credit.index:
            df_credit.loc["지출"] = [0]
        df_credit = df_credit.sort_index()
        y = df_credit.values.flatten()
        x = df_credit.index.tolist()
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.cur_crd.addWidget(self.canvas)
        ax = self.fig.add_subplot(111)
        ax.bar(x, y, color=list(mcolors.TABLEAU_COLORS.values())[:len(x)])
        ax.yaxis.set_visible(False)
        for p in ax.patches:
            left, bottom, width, height = p.get_bbox().bounds
            ax.annotate("{} 원".format("{:,}".format(int(height))), (left + width / 2, height * 1.01), ha='center')
        ax.set_title("Monthly spending status")
        self.canvas.draw()


        # Details
    def details(self):
        self.dateedit.setDate(QDate.currentDate())
        self.dateedit2.setDate(QDate.currentDate())
        self.day_check.stateChanged.connect(self.chk)
        self.month_check.stateChanged.connect(self.chk)

        self.detail_table.customContextMenuRequested.connect(self.delete)
        self.detail_table.setColumnHidden(0, True)

        self.use_c = {0:" ", 1:"수입", 2:"지출"}
        self.use_combo.addItems(self.use_c.values())

        self.use_combo.activated.connect(self.combo)
        self.list_c1 = {0:" ", 1:"급여", 2:"상여금", 3:"이자", 4:"기타"}
        self.list_c2 = {0:" ", 1:"월세", 2:"통신비", 3:"보험료", 4:"저축/적금", 5:"식비", 6:"교통비", 7:"생활용품", 8:"의료비", 9:"기타"}

        self.type_combo.activated.connect(self.accountCombo)
        self.list_t = {0:" ", 1:"현금/체크카드", 2:"신용카드"}
        self.type_combo.addItems(self.list_t.values())

        self.register_btn.clicked.connect(self.register)

        sql = "select * from {}".format("account_book")
        self.all = []
        cur = self.dbConn.cursor()
        cur.execute(sql)
        for i, row in enumerate(cur):
            self.detail_table.insertRow(i)
            self.all.append(row)
            for c, item in enumerate(row):
                self.detail_table.setItem(i, c, QTableWidgetItem(str(item)))
        self.select_btn.clicked.connect(self.select)



        # Report
    def report(self):
        def AddDays(sourceDate, count):
            targetDate = sourceDate + timedelta(days=count)
            return targetDate

        def GetWeekFirstDate(sourceDate):
            temporaryDate = datetime(sourceDate.year, sourceDate.month, sourceDate.day)
            weekDayCount = temporaryDate.weekday()
            startDate = AddDays(temporaryDate, -weekDayCount)
            endDate = AddDays(temporaryDate, -weekDayCount+6)
            return startDate, endDate

        date = GetWeekFirstDate(datetime.today())
        sql_im = "select use_date, sum(use_cost) from account_book where use_type='수입' and use_date between '{}' and '{}' group by use_date".format(
            date[0], date[1])
        sql_ex = "select use_date, sum(use_cost) from account_book where use_type='지출' and use_date between '{}' and '{}' group by use_date".format(
            date[0], date[1])
        w_df_im = pd.read_sql(sql_im, self.dbConn, index_col="use_date")
        w_df_ex = pd.read_sql(sql_ex, self.dbConn, index_col="use_date")
        d1 = datetime.date(date[0])
        d2 = datetime.date(date[1])
        diff = d2 - d1
        days = [d1 + timedelta(i) for i in range(diff.days + 1)]
        for i in days:
            if i not in w_df_im.index:
                w_df_im.loc[i] = 0
            if i not in w_df_ex.index:
                w_df_ex.loc[i] = 0
        w_df_im = w_df_im.sort_index()
        w_df_ex = w_df_ex.sort_index()
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.w_r.addWidget(self.canvas)
        y1 = w_df_im.values.flatten()
        y2 = w_df_ex.values.flatten()
        x = days
        ax = self.fig.add_subplot(111)
        ax.yaxis.set_visible(False)
        ax.plot(x, y1, color="cornflowerblue")
        ax.plot(x, y2, color="tomato")
        for i, j in zip(x, y1):
            ax.annotate("{} 원".format("{:,}".format(j)), xy=(i, j), va="top")
        for i, j in zip(x, y2):
            ax.annotate("{} 원".format("{:,}".format(j)), xy=(i, j), va="bottom")
        ax.legend(["수입", "지출"])
        ax.set_title("Weekly status")
        self.canvas.draw()

        y = str(datetime.today().year)
        sql_im = "select month(use_date) as use_date, sum(use_cost) from account_book where use_type='수입' and use_date between '{}' and '{}' group by month(use_date)".format(
            y+"-01-01", y+"-12-31")
        sql_ex = "select month(use_date) as use_date, sum(use_cost) from account_book where use_type='지출' and use_date between '{}' and '{}' group by month(use_date)".format(
            y+"-01-01", y+"-12-31")
        m_df_im = pd.read_sql(sql_im, self.dbConn, index_col="use_date")
        m_df_ex = pd.read_sql(sql_ex, self.dbConn, index_col="use_date")
        months = [int("%0.2d" % i) for i in range(1, 13)]
        for i in months:
            if i not in m_df_im.index:
                m_df_im.loc[i] = 0
            if i not in m_df_ex.index:
                m_df_ex.loc[i] = 0
        m_df_im = m_df_im.sort_index()
        m_df_ex = m_df_ex.sort_index()
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.m_r.addWidget(self.canvas)
        y1 = m_df_im.values.flatten()
        y2 = m_df_ex.values.flatten()
        x = months
        ax = self.fig.add_subplot(111)
        ax.yaxis.set_visible(False)
        ax.plot(x, y1, color="cornflowerblue")
        ax.plot(x, y2, color="tomato")
        for i, j in zip(x, y1):
            ax.annotate("{} 원".format("{:,}".format(j)), xy=(i, j), va="top")
        for i, j in zip(x, y2):
            ax.annotate("{} 원".format("{:,}".format(j)), xy=(i, j), va="bottom")
        ax.legend(["수입", "지출"])
        ax.set_title("Monthly status")
        self.canvas.draw()

        sql_im = "select list, sum(use_cost) as use_cost from account_book where use_type = '수입' group by list"
        sql_ex = "select list, sum(use_cost) as use_cost from account_book where use_type = '지출' group by list"
        df_im = pd.read_sql(sql_im, self.dbConn, index_col="list")
        df_ex = pd.read_sql(sql_ex, self.dbConn, index_col="list")

        y1 = df_im.values.flatten()
        x1 = df_im.index.tolist()
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.im_report.addWidget(self.canvas)
        ax1 = self.fig.add_subplot(111)
        ax1.pie(y1, labels=x1, autopct="%.1f%%")
        ax1.legend(loc="lower right", ncol=2, bbox_to_anchor=(0, 0), prop={'size': 6})
        self.canvas.draw()

        y2 = df_ex.values.flatten()
        x2 = df_ex.index.tolist()
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ex_report.addWidget(self.canvas)
        ax2 = self.fig.add_subplot(111)
        ax2.pie(y2, labels=x2, autopct="%1.1f%%")
        ax2.legend(loc="lower right", ncol=2, bbox_to_anchor=(0, 0), prop={'size': 6})
        self.canvas.draw()

        sql = "select account, count(*) from account_book where type = '현금/체크카드' group by account"
        df_check = pd.read_sql(sql, self.dbConn, index_col="account")
        df_check = df_check.sort_values(by="count(*)", ascending=False)
        y = df_check.values.flatten()
        x = [i.split("/")[0] for i in df_check.index.tolist()]
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.check_report.addWidget(self.canvas)
        ax = self.fig.add_subplot(111)
        ax.bar(x, y, color=list(mcolors.TABLEAU_COLORS.values())[:len(x)])
        ax.yaxis.set_visible(False)
        for p in ax.patches:
            left, bottom, width, height = p.get_bbox().bounds
            ax.annotate("{} 번".format("{:,}".format(int(height))), (left + width / 2, height * 1.01), ha='center')
        self.canvas.draw()

        sql = "select account, count(*) from account_book where type = '신용카드' group by account"
        df_credit = pd.read_sql(sql, self.dbConn, index_col="account")
        df_credit = df_credit.sort_values(by="count(*)", ascending=False)
        y = df_credit.values.flatten()
        x = [i.split("/")[0] for i in df_credit.index.tolist()]
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.credit_report.addWidget(self.canvas)
        ax = self.fig.add_subplot(111)
        ax.bar(x, y, color=list(mcolors.TABLEAU_COLORS.values())[:len(x)])
        ax.yaxis.set_visible(False)
        for p in ax.patches:
            left, bottom, width, height = p.get_bbox().bounds
            ax.annotate("{} 번".format("{:,}".format(int(height))), (left + width / 2, height * 1.01), ha='center')
        self.canvas.draw()


        # Setting
        self.lineEdit.setHidden(True)
        self.lineEdit_2.setHidden(True)
        self.lineEdit_3.setHidden(True)
        self.lineEdit_5.setHidden(True)

        self.setting_combo.activated.connect(self.setting)
        self.save_btn.clicked.connect(self.save)

        self.account_type = {0:" "}
        sql = "select * from {}".format("account_info")
        cur = self.dbConn.cursor()
        cur.execute(sql)
        for i, row in enumerate(cur):
            self.check_table.insertRow(i)
            tmp = "{}/{}".format(row[1], row[2])
            self.account_type[i+1] = tmp
            for c, item in enumerate(row):
                self.check_table.setItem(i, c, QTableWidgetItem(str(item)))

        self.credit_type = {0:" "}
        sql = "select * from {}".format("credit_info")
        cur = self.dbConn.cursor()
        cur.execute(sql)
        for i, row in enumerate(cur):
            self.credit_table.insertRow(i)
            tmp = "{}/{}".format(row[1], row[-1])
            self.credit_type[i+1] = tmp
            for c, item in enumerate(row):
                self.credit_table.setItem(i, c, QTableWidgetItem(str(item)))

        self.check_table.customContextMenuRequested.connect(self.delete2)
        self.check_table.setColumnHidden(0, True)
        self.credit_table.customContextMenuRequested.connect(self.delete3)
        self.credit_table.setColumnHidden(0, True)


########################################################################################################################
    def chk(self, state):
        if state == Qt.Checked:
            if self.sender() == self.day_check:
                self.month_check.setChecked(False)
                self.dateedit2.setDisplayFormat("yyyy-MM-dd")

            elif self.sender() == self.month_check:
                self.day_check.setChecked(False)
                self.dateedit2.setDisplayFormat("yyyy-MM")


    def delete(self, position):
        self.menu = QMenu()
        self.delete_action = self.menu.addAction("삭제")
        action = self.menu.exec(self.detail_table.mapToGlobal(position))
        if action == self.delete_action:
            self.row = self.detail_table.selectedIndexes()[0].row()+1
            self.detail_table.removeRow(self.row-1)

            sql = "delete from account_book where no = {}".format(self.row)
            cur = self.dbConn.cursor()
            cur.execute(sql)
            self.dbConn.commit()

            sql = "update account_book set no = no-1 where no > {}".format(self.row)
            cur = self.dbConn.cursor()
            cur.execute(sql)
            self.dbConn.commit()

        self.C()
        self.main()

        self.report()

    def select(self):
        if self.day_check.isChecked():
           text = self.dateedit2.date().toString("yyyy-MM-dd")
           sql = "select * from {} where {} = '{}'".format("account_book", "use_date", text)
           self.detail_table.setRowCount(0)
           cur = self.dbConn.cursor()
           cur.execute(sql)
           for i in cur:
               rC = self.detail_table.rowCount()
               self.detail_table.insertRow(rC)
               for c, item in enumerate(i):
                   self.detail_table.setItem(rC, c, QTableWidgetItem(str(item)))

        elif self.month_check.isChecked():
           text = self.dateedit2.date().toString("yyyy-MM")
           sql = "select * from {} where {} like '{}%'".format("account_book", "use_date", text)
           self.detail_table.setRowCount(0)
           cur = self.dbConn.cursor()
           cur.execute(sql)
           for i in cur:
               rC = self.detail_table.rowCount()
               self.detail_table.insertRow(rC)
               for c, item in enumerate(i):
                   self.detail_table.setItem(rC, c, QTableWidgetItem(str(item)))

        else:
            self.dateedit2.setDate(QDate.currentDate())
            sql = "select * from {}".format("account_book")
            self.detail_table.setRowCount(0)
            cur = self.dbConn.cursor()
            cur.execute(sql)
            for i in cur:
                rC = self.detail_table.rowCount()
                self.detail_table.insertRow(rC)
                for c, item in enumerate(i):
                    self.detail_table.setItem(rC, c, QTableWidgetItem(str(item)))

    def combo(self):
        text = self.use_combo.currentText()
        self.list_combo.clear()
        if text == "수입":
            self.list_combo.addItems(self.list_c1.values())
        elif text == "지출":
            self.list_combo.addItems(self.list_c2.values())

    def accountCombo(self):
        text = self.type_combo.currentText()
        self.account_combo.clear()
        if text == "현금/체크카드":
           self.account_combo.addItems(self.account_type.values())
        elif text == "신용카드":
            self.account_combo.addItems(self.credit_type.values())

    def register(self):
        self.rC = self.detail_table.rowCount()
        self.row = (self.rC+1,
                    self.dateedit.date().toString("yyyy-MM-dd"),
                    self.use_combo.currentText(),
                    self.list_combo.currentText(),
                    self.type_combo.currentText(),
                    self.account_combo.currentText(),
                    self.cost.text(),
                    self.memo.text())
        self.detail_table.insertRow(self.rC)
        for c, item in enumerate(self.row):
            self.detail_table.setItem(self.rC, c, QTableWidgetItem(str(item)))

        sql = "insert into {} values {}".format("account_book", self.row)
        cur = self.dbConn.cursor()
        cur.execute(sql)
        self.dbConn.commit()

        if self.type_combo.currentText() == "현금/체크카드":
            if self.use_combo.currentText() == "수입":
                sql = "update account_info set balance = balance + {} where account_number = {}".format(int(self.cost.text()), self.account_combo.currentText().split("/")[1])
                cur = self.dbConn.cursor()
                cur.execute(sql)
                self.dbConn.commit()
            elif  self.use_combo.currentText() == "지출":
                sql = "update account_info set balance = balance - {} where account_number = {}".format(int(self.cost.text()), self.account_combo.currentText().split("/")[1])
                cur = self.dbConn.cursor()
                cur.execute(sql)
                self.dbConn.commit()

        self.use_combo.setCurrentIndex(0)
        self.list_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.account_combo.setCurrentIndex(0)
        self.cost.clear()
        self.memo.clear()

        self.C()
        self.main()
        self.report()

    def C(self):
        for i in [self.cur_chk, self.cur_crd, self.w_r, self.m_r, self.im_report, self.ex_report, self.check_report, self.credit_report]:
            for j in reversed(range(i.count())):
                i.itemAt(j).widget().setParent(None)

        for i in [self.check_table, self.credit_table]:
            i.setRowCount(0)



#######################################################################################################################
    def setting(self):
        self.lineEdit.setHidden(False)
        self.lineEdit_2.setHidden(False)
        self.lineEdit_3.setHidden(False)
        self.lineEdit_5.setHidden(False)

        text = self.setting_combo.currentText()
        if text == "체크카드/현금":
            self.company_lb.setText("은행")
            self.account_lb.setText("계좌번호")
            self.cost_withdraw.setText("잔액")
            self.memo_lb.setText("메모")
        elif text == "신용카드":
            self.company_lb.setText("카드사")
            self.account_lb.setText("출금계좌")
            self.cost_withdraw.setText("출금일")
            self.memo_lb.setText("메모")

    def save(self):
        self.text = self.setting_combo.currentText()
        if self.text == "체크카드/현금":
            self.table = "account_info"
            self.rC = self.check_table.rowCount()
            self.row = (self.rC+1, self.lineEdit.text(), self.lineEdit_2.text(), self.lineEdit_3.text(), self.lineEdit_5.text())
            self.check_table.insertRow(self.rC)
            for c, item in enumerate(self.row):
                self.check_table.setItem(self.rC, c, QTableWidgetItem(str(item)))
            self.account_type[self.rC+1] = "{}/{}".format(self.row[1], self.row[2])

        elif self.text == "신용카드":
            self.table = "credit_info"
            self.rC = self.credit_table.rowCount()
            self.row = (self.rC+1, self.lineEdit.text(), self.lineEdit_2.text(), self.lineEdit_3.text(), self.lineEdit_5.text())
            self.credit_table.insertRow(self.rC)
            for c, item in enumerate(self.row):
                self.credit_table.setItem(self.rC, c, QTableWidgetItem(str(item)))
            self.credit_type[self.rC+1] = "{}/{}".format(self.row[1], self.row[-1])

        sql = "insert into {} values {}".format(self.table, self.row)
        cur = self.dbConn.cursor()
        cur.execute(sql)
        self.dbConn.commit()

        self.setting_combo.setCurrentIndex(0)
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_5.clear()

    def delete2(self, position):
        self.menu = QMenu()
        self.delete_action = self.menu.addAction("삭제")
        action = self.menu.exec(self.check_table.mapToGlobal(position))
        if action == self.delete_action:
            self.row = self.check_table.selectedIndexes()[0].row()+1
            del self.account_type[self.row]
            self.check_table.removeRow(self.row-1)

            sql = "delete from account_info where no = {}".format(self.row)
            cur = self.dbConn.cursor()
            cur.execute(sql)
            self.dbConn.commit()

            sql = "update account_info set no = no-1 where no > {}".format(self.row)
            cur = self.dbConn.cursor()
            cur.execute(sql)
            self.dbConn.commit()

        self.C()
        self.main()
        self.report()

    def delete3(self, position):
        self.menu = QMenu()
        self.delete_action = self.menu.addAction("삭제")
        action = self.menu.exec(self.credit_table.mapToGlobal(position))
        if action == self.delete_action:
            self.row = self.credit_table.selectedIndexes()[0].row() + 1
            del self.credit_type[self.row]
            self.credit_table.removeRow(self.row-1)

            sql = "delete from credit_info where no = {}".format(self.row)
            cur = self.dbConn.cursor()
            cur.execute(sql)
            self.dbConn.commit()

            sql = "update credit_info set no = no-1 where no > {}".format(self.row)
            cur = self.dbConn.cursor()
            cur.execute(sql)
            self.dbConn.commit()

        self.C()
        self.main()
        self.report()



form_class = loadUiType("login.ui")[0]


class login(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.login.clicked.connect(self.conn)
        self.setWindowTitle("Login")

    def conn(self):
        self.u = self.id.text()
        self.p = self.pwd.text()
        try:
            self.dbConn = pymysql.connect(user="root",
                                          password=self.p,
                                          host="127.0.0.1",
                                          db="mysql",
                                          charset="UTF8")

            cur = self.dbConn.cursor()
            sql1 = "select user from user"
            cur.execute(sql1)

            if self.u not in [i[0] for i in cur]:
                QMessageBox.information(
                    self, 'Error', "입력하신 정보가 없습니다. 정보를 생성하겠습니다.",
                    QMessageBox.Yes)
                cur.execute("create user {}".format(self.u))
                self.dbConn.commit()



            buttonReply = QMessageBox.information(
                self, 'Success', "DB 연결 성공!", QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes:
                try:
                    self.dbConn = pymysql.connect(user="root",
                                                  password=self.p,
                                                  host="127.0.0.1",
                                                  db="account",
                                                  charset="UTF8")
                    self.close()
                    dlg = Home()
                    dlg.exec_()

                except:
                    Reply = QMessageBox.information(
                        self, 'Error', "Account DB가 존재하지 않습니다. Account DB를 생성하시겠습니까?",
                        QMessageBox.Yes
                    )
                    if Reply == QMessageBox.Yes:
                        self.dbConn = pymysql.connect(user="root",
                                                      password=self.p,
                                                      host="127.0.0.1",
                                                      db="mysql",
                                                      charset="UTF8")
                        cur = self.dbConn.cursor()
                        sql1 = "create database account"
                        cur.execute(sql1)
                        self.dbConn.commit()

                        self.dbConn = pymysql.connect(user="root",
                                                      password=self.p,
                                                      host="127.0.0.1",
                                                      db="account",
                                                      charset="UTF8"
                                                      )

                        sql5 = "create table account_book (no int, use_date date, use_type varchar(50), list varchar(50), type varchar(50), account varchar(50), use_cost int, memo varchar(50), primary key (no))"
                        sql6 = "create table account_info (no int, bank_name varchar(50), account_number varchar(50), balance int, memo varchar(50), primary key (no))"
                        sql7 = "create table credit_info (no int, credit_bank varchar(50), withdraw_account varchar(50), withdraw_date int, memo varchar(50), primary key (no))"
                        sql8 = "create table setting_info (import varchar(50), export varchar(50))"
                        for i in [sql5, sql6, sql7, sql8]:
                            cur = self.dbConn.cursor()
                            cur.execute(i)
                            self.dbConn.commit()


        except:
            Reply = QMessageBox.information(
                self, 'Error', "입력하신 정보가 없습니다.",
                QMessageBox.Yes
            )


app=QApplication(sys.argv)
myWindow=login()
myWindow.show()
app.exec_()
