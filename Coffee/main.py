import sys
import sqlite3
from PyQt5.QtSql import QSqlDatabase, QSqlRelationalTableModel, QSqlRelation
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, \
    QInputDialog
from PyQt5.QtCore import Qt
from MainWindow import Ui_MainWindow
from addEditCoffeeForm import Ui_Dialog


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class AddEditCoffee(QDialog, Ui_Dialog):
    def __init__(self, data):
        super().__init__()
        self.setupUi(self)
        self.box.removeButton(self.box.buttons()[0])
        self.btn_ok.clicked.connect(self.check_data)
        self.data = []
        con = sqlite3.connect('data/coffee.sqlite').cursor()
        types = con.execute('''SELECT 
        * FROM CoffeeTypes''').fetchall()
        self.coffee_type.addItems([f'{i[0]}\t{i[1]}' for i in types])
        roast = con.execute('SELECT * FROM RoastDegree').fetchall()
        self.coffee_roast.addItems([f'{i[0]} {i[1]}' for i in roast])
        mass = con.execute('SELECT * FROM CoffeeWeights').fetchall()
        self.coffee_mass.addItems([f'{i[0]}\t{i[1]}' for i in mass])
        self.rad1.setChecked(True)
        if data:
            self.loadData(data)

    def loadData(self, data):
        self.coffee_sort.setText(data[0])
        typee = sqlite3.connect('data/coffee.sqlite').cursor().execute(f'''
        SELECT Abbreviation FROM CoffeeTypes WHERE 
        RusName = "{data[1]}"''').fetchone()
        self.coffee_type.setCurrentText(f'{typee[0]}\t{data[1]}')
        roasted = [self.coffee_roast.itemText(i) for i in
                   range(self.coffee_roast.count())]
        self.coffee_roast.setCurrentText(
            [i for i in roasted if data[2] in i][0])
        if data[3] == 'Молотый':
            self.rad1.setChecked(True)
        else:
            self.rad2.setChecked(True)
        self.coffee_taste.appendPlainText(data[4])
        self.coffee_price.setValue(data[5])
        masses = [self.coffee_mass.itemText(i) for i in
                  range(self.coffee_mass.count())]
        self.coffee_mass.setCurrentText([i for i in masses
                                         if str(data[-1]) in i][0])

    def check_data(self):
        if self.coffee_sort.text():
            name = self.coffee_sort.text()
            typee = self.coffee_type.currentText().split('\t')[0]
            roast = int(self.coffee_roast.currentText().split()[0])
            grain = 2 if self.rad1.isChecked() else 1
            taste = self.coffee_taste.toPlainText()
            price = self.coffee_price.value()
            mass = self.coffee_mass.currentText().split('\t')[0]
            self.data = [name, typee, roast, grain, taste, price, mass]
            self.accept()
        else:
            QMessageBox.warning(self, 'Внимание', 'Названия сорта не может '
                                                  'быть пустой строкой.')

    def get_taste(self):
        text = QInputDialog.getMultiLineText(self, 'Опишите вкус',
                                             'Опишите вкус сорта кофе',
                                             self.coffee_taste.toPlainText())
        self.coffee_taste.clear()
        self.coffee_taste.appendPlainText(text)


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect('data/coffee.sqlite')
        types = self.con.cursor().execute('''SELECT RusName FROM 
        CoffeeTypes''').fetchall()
        self.view.doubleClicked.connect(self.giveInfo)
        self.rows = 0
        self.combo.addItems(['Все'] + [i[0] for i in types])
        self.combo.currentTextChanged.connect(self.reloadData)
        self.btn_add.clicked.connect(self.addCoffee)
        self.btn_edit.clicked.connect(self.editCoffee)
        self.btn_del.clicked.connect(self.delCoffee)
        self.initUI()

    def initUI(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('data/coffee.sqlite')
        db.open()
        titles = ['ID', 'Сорт', 'Вид', 'Обжарка', 'Зерна',
                  'Вкус', 'Цена', 'Масса в граммах']
        model = QSqlRelationalTableModel(self, db)
        model.setTable('Coffee')
        model.setRelation(2, QSqlRelation('CoffeeTypes', 'Abbreviation',
                                          'RusName'))
        model.setRelation(3, QSqlRelation('RoastDegree', 'ID', 'Name'))
        model.setRelation(4, QSqlRelation('GrainCondition', 'ID', 'Condition'))
        model.setRelation(7, QSqlRelation('CoffeeWeights', 'Letter',
                                          'WeightGrams'))
        for i in range(8):
            model.setHeaderData(i, Qt.Horizontal, titles[i])
        model.select()
        self.rows = model.rowCount()
        self.view.setModel(model)

    def reloadData(self):
        for i in range(self.rows):
            self.view.showRow(i)

        name = self.sender().currentText()
        if name != 'Все':
            for i in range(self.rows):
                if self.view.model().index(i, 2).data() != name:
                    self.view.hideRow(i)

    def giveInfo(self, item):
        if item.column() == 5:
            QMessageBox.information(self, 'Вкус', self.view.model().index(
                item.row(), item.column()).data())

    def delCoffee(self):
        ids = list(set([i.row() for i in
                        self.view.selectionModel().selectedIndexes()]))
        ids = [int(self.view.model().index(i, 0).data()) for i in ids]
        do_or_not = QMessageBox.question(
            self, '', "Действительно удалить элементы?",
            QMessageBox.Yes, QMessageBox.No)
        if do_or_not == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute(f"DELETE FROM Coffee WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
            self.initUI()

    def addCoffee(self):
        ch = AddEditCoffee([])
        if ch.exec_():
            data = ch.data
            self.con.cursor().execute(f'''INSERT INTO Coffee (Name, Type, 
            Roast, Grains, Taste, Price, Mass) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                      data)
            self.con.commit()
        self.initUI()

    def editCoffee(self):
        rows = list(set([
            i.row() for i in self.view.selectionModel().selectedIndexes()]))
        if len(rows) == 1:
            data = [self.view.model().index(rows[0], i).data() for i in
                    range(0, 8)]
            ch = AddEditCoffee(data[1:])
            if ch.exec_():
                self.con.cursor().execute(f'''UPDATE Coffee SET Name = ?, 
            Type = ?, Roast = ?, Grains = ?, Taste = ?, Price = ?, Mass = ? 
            WHERE ID = {data[0]}''', ch.data)
                self.con.commit()
                self.initUI()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())