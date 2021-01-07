import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QPushButton, \
    QScrollArea, QVBoxLayout, QWidget
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont

USER_NAME = ''
EMAIL = ''
USERID = 1
IMAGE = 'no_avatar.png'
CON = sqlite3.connect('App.db')
THEME = 'BLACK'
CHATID = 0

theme = open('theme.txt', 'r')
text = theme.read()
if text == 'WHITE':
    THEME = 'WHITE'
else:
    THEME = 'BLACK'


def to_binary(filename):
    with open(filename, 'rb') as file:
        data = file.read()
    return data


class MyWidget(QMainWindow):
    def __init__(self):
        global USERID, USER_NAME, IMAGE, CON
        self.like1 = False
        self.like2 = False
        self.IMG1_ID = 0
        self.IMG2_ID = 0
        self.skip = -2
        self.COUNT1 = 0
        self.COUNT2 = 0
        self.add = True
        super().__init__()
        uic.loadUi(r'main.ui', self)
        if THEME == "BLACK":
            self.setStyleSheet('background-color: rgb(0, 0, 0)')
            self.comment_label1.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')
            self.comment_label2.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')
            self.name_1.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.name_2.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.error_label.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
        cur = CON.cursor()
        self.setWindowIcon(QIcon(r'logo.jpg'))
        self.username_label.setText(USER_NAME)
        res = cur.execute("""SELECT image FROM Users WHERE id = ?""", (USERID,)).fetchone()
        image = res[0]
        pixmap = QPixmap()
        pixmap.loadFromData(image, 'jpg')
        self.acc_btn.setIcon(QIcon(pixmap))
        self.acc_btn.setIconSize(QSize(100, 100))
        self.acc_btn.clicked.connect(self.acc_func)
        self.acc_btn.setToolTip('Изменение аккаунта')
        self.chat_btn.clicked.connect(self.chat)
        self.next.clicked.connect(self.next_posts)
        self.prev.clicked.connect(self.prev_posts)
        self.add_pic.clicked.connect(self.add_picture)
        self.error_label.hide()
        self.like_btn1.clicked.connect(self.add_like)
        self.like_btn2.clicked.connect(self.add_like)
        self.like_btn1.hide()
        self.like_btn2.hide()
        self.lcdNumber_1.hide()
        self.lcdNumber_2.hide()
        self.next_posts()

    def add_like(self):
        cur = CON.cursor()
        if self.sender() == self.like_btn1:
            if not self.like1:
                cur.execute("""INSERT INTO Likes(image_id, user_id) VALUES (?, ?) """,
                            (self.IMG1_ID, USERID))
                self.like1 = True
                CON.commit()
                self.like_btn1.setIcon(QIcon("like_clicked.png"))
                self.like_btn1.setIconSize(QSize(35, 35))
                self.COUNT1 += 1
                self.lcdNumber_1.display(self.COUNT1)
                self.lcdNumber_1.display(self.COUNT1)
            else:
                cur.execute("""DELETE FROM Likes WHERE image_id = ? AND user_id = ?""",
                            (self.IMG1_ID, USERID))
                self.like1 = False
                CON.commit()
                self.COUNT1 -= 1
                self.like_btn1.setIcon(QIcon("like.png"))
                self.like_btn1.setIconSize(QSize(35, 35))
                self.lcdNumber_1.display(self.COUNT1)
        else:
            if not self.like2:
                cur.execute("""INSERT INTO Likes(image_id, user_id) VALUES (?, ?) """,
                            (self.IMG2_ID, USERID))
                self.like2 = True
                CON.commit()
                self.like_btn2.setIcon(QIcon("like_clicked.png"))
                self.like_btn2.setIconSize(QSize(35, 35))
                self.COUNT2 += 1
                self.lcdNumber_2.display(self.COUNT2)
            else:
                cur.execute("""DELETE FROM Likes WHERE image_id = ? AND user_id = ?""",
                            (self.IMG2_ID, USERID))
                self.like2 = False
                self.like_btn2.setIcon(QIcon("like.png"))
                self.like_btn2.setIconSize(QSize(35, 35))
                CON.commit()
                self.COUNT2 -= 1
                self.lcdNumber_2.display(self.COUNT2)

    def next_posts(self):
        if self.add:
            self.skip += 2
            self.show_posts()

    def prev_posts(self):
        if self.skip >= 2:
            self.skip -= 2
            self.show_posts()

    def show_posts(self):
        cur = CON.cursor()
        print(self.skip)
        res = cur.execute("""SELECT Images.image, Users.image, Images.text, 
        Users.user, Images.id_image FROM Images  INNER JOIN Users ON 
        Images.author_id = Users.id ORDER BY Images.id_image DESC LIMIT 2 OFFSET ?""",
                          (self.skip,)).fetchall()
        step = 0
        if not bool(res):
            self.skip -= 2
            self.add = False
            self.error_label.show()
        else:
            self.add = True
        if len(res) == 1:
            for elem in res:
                self.pic1.show()
                self.author_1.show()
                self.name_1.show()
                self.comment_label1.show()
                self.like_btn1.show()
                self.lcdNumber_1.show()
                pixmap_main_image = QPixmap()
                pixmap_main_image.loadFromData(elem[0], 'jpg')
                pixmap_user_image = QPixmap()
                pixmap_user_image.loadFromData(elem[1], 'jpg')
                self.name_1.setText(elem[3])
                self.comment_label1.setText(elem[2])
                self.author_1.setIcon(QIcon(pixmap_user_image))
                self.author_1.setIconSize(QSize(70, 70))
                self.pic1.setPixmap(pixmap_main_image)
                self.pic1.setScaledContents(True)
                self.COUNT1 = len(cur.execute("""SELECT * FROM Likes WHERE image_id = ?""", (elem[4],)).fetchall())
                self.lcdNumber_1.display(self.COUNT1)
                like = bool(cur.execute("""SELECT * FROM Likes WHERE image_id = ? AND user_id = ?""",
                                        (elem[4], USERID)).fetchone())
                if like:
                    self.like_btn1.setIcon(QIcon("like_clicked.png"))
                    self.like_btn1.setIconSize(QSize(35, 35))
                    self.like1 = True
                else:
                    self.like_btn1.setIcon(QIcon("like.png"))
                    self.like_btn1.setIconSize(QSize(35, 35))
                    self.like1 = False
                self.IMG1_ID = elem[4]
            self.name_2.hide()
            self.comment_label2.hide()
            self.author_2.hide()
            self.pic2.hide()
            self.like_btn2.hide()
            self.lcdNumber_2.hide()
            self.IMG2_ID = 0
        else:
            for elem in res:
                if step == 0:
                    self.pic1.show()
                    self.author_1.show()
                    self.name_1.show()
                    self.comment_label1.show()
                    self.like_btn1.show()
                    self.lcdNumber_1.show()
                    pixmap_main_image = QPixmap()
                    pixmap_main_image.loadFromData(elem[0], 'jpg')
                    pixmap_user_image = QPixmap()
                    pixmap_user_image.loadFromData(elem[1], 'jpg')
                    self.name_1.setText(elem[3])
                    self.comment_label1.setText(elem[2])
                    self.author_1.setIcon(QIcon(pixmap_user_image))
                    self.author_1.setIconSize(QSize(70, 70))
                    self.pic1.setPixmap(pixmap_main_image)
                    self.pic1.setScaledContents(True)
                    self.COUNT1 = len(cur.execute("""SELECT * FROM Likes WHERE image_id = ?""", (elem[4],)).fetchall())
                    self.lcdNumber_1.display(self.COUNT1)
                    like = bool(
                        cur.execute("""SELECT * FROM LIKES WHERE image_id = ? AND user_id = ?""",
                                    (elem[4], USERID)).fetchone())
                    if like:
                        self.like_btn1.setIcon(QIcon("like_clicked.png"))
                        self.like_btn1.setIconSize(QSize(35, 35))
                        self.like1 = True
                    else:
                        self.like1 = False
                        self.like_btn1.setIcon(QIcon("like.png"))
                        self.like_btn1.setIconSize(QSize(35, 35))
                    self.IMG1_ID = elem[4]
                    step += 1
                else:
                    self.pic2.show()
                    self.author_2.show()
                    self.name_2.show()
                    self.comment_label2.show()
                    self.like_btn2.show()
                    self.lcdNumber_2.show()
                    pixmap_main_image = QPixmap()
                    pixmap_main_image.loadFromData(elem[0], 'jpg')
                    pixmap_user_image = QPixmap()
                    pixmap_user_image.loadFromData(elem[1], 'jpg')
                    self.name_2.setText(elem[3])
                    self.comment_label2.setText(elem[2])
                    self.author_2.setIcon(QIcon(pixmap_user_image))
                    self.author_2.setIconSize(QSize(70, 70))
                    self.pic2.setPixmap(pixmap_main_image)
                    self.pic2.setScaledContents(True)
                    self.COUNT2 = len(cur.execute("""SELECT * FROM Likes WHERE image_id = ?""", (elem[4],)).fetchall())
                    self.lcdNumber_2.display(self.COUNT1)
                    like = bool(
                        cur.execute("""SELECT * FROM LIKES WHERE image_id = ? AND user_id = ?""",
                                    (elem[4], USERID)).fetchone())
                    if like:
                        self.like2 = True
                        self.like_btn2.setIcon(QIcon("like_clicked.png"))
                        self.like_btn2.setIconSize(QSize(35, 35))
                    else:
                        self.like2 = False
                        self.like_btn2.setIcon(QIcon("like.png"))
                        self.like_btn2.setIconSize(QSize(35, 35))
                    self.IMG2_ID = elem[4]

    def choose_image(self):
        global IMAGE
        image = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                            'Картинка jpg (*.jpg);;jpeg (*.jpeg)')[0]
        self.image.setText(image)
        IMAGE = image

    def chat(self):
        self.chat_window = Chats()
        self.chat_window.show()

    def acc_func(self):
        self.acc_window = Account()
        self.acc_window.show()
        self.hide()

    def add_picture(self):
        self.add_window = Add_Picture()
        self.add_window.show()
        self.hide()


class Account(QMainWindow):
    def __init__(self):
        global USER_NAME, EMAIL, IMAGE
        super().__init__()
        uic.loadUi(r'account.ui', self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        if THEME == 'BLACK':
            self.setStyleSheet('background-color: rgb(0, 0, 0)')
            self.login.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.email.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
        self.avatar.clicked.connect(self.change)
        cur = CON.cursor()
        res = cur.execute("""SELECT image FROM Users WHERE id = ?""", (USERID,)).fetchone()
        image = res[0]
        pixmap = QPixmap()
        pixmap.loadFromData(image, 'jpg')
        self.avatar.setIcon(QIcon(pixmap))
        self.avatar.setIconSize(QSize(100, 100))
        self.avatar.setToolTip('Изменение аккаунта')
        self.setWindowIcon(QIcon(r'logo.jpg'))
        self.exit_btn.clicked.connect(self.exit_exe)
        self.home_btn.setIcon(QIcon(r'back.png'))
        self.home_btn.setIconSize(QSize(40, 40))
        self.home_btn.clicked.connect(self.home)
        self.login.setText(USER_NAME)
        self.email.setText(EMAIL)
        self.delete_btn.clicked.connect(self.delete_acc)
        self.switch_btn.clicked.connect(self.change_theme)
        self.switch_btn.setIcon(QIcon("switch.png"))
        self.switch_btn.setIconSize(QSize(70, 70))

    def change(self):
        self.hide()
        self.widget = Change()
        self.widget.show()

    def exit_exe(self):
        msg = QMessageBox(self)

        msg.setFont(QFont('Comfortaa', 16))
        msg.setStyleSheet('color: black; background-color: white')
        msg.setText('Вы уверены, что хотите выйти?')
        msg.setWindowTitle('Выход')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = msg.exec_()
        if retval == QMessageBox.Yes:
            self.close()
        else:
            pass

    def home(self):
        self.hide()
        self.mywidget = MyWidget()
        self.mywidget.show()

    def closeEvent(self, event):
        event.accept()

    def delete_acc(self):
        global USERID
        msg = QMessageBox(self)
        msg.setFont(QFont('Comfortaa', 16))
        msg.setStyleSheet('color: black; background-color: white')
        msg.setText('Вы уверены, что хотите удалить аккаунт?')
        msg.setWindowTitle('Удаление аккаунта')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = msg.exec_()
        if retval == QMessageBox.Yes:
            cur = CON.cursor()
            cur.execute("DELETE FROM Users WHERE id = ?""", (USERID,))
            cur.execute("""DELETE FROM Messages WHERE user_id = ?""", (USERID,))
            images = cur.execute("""SELECT id_image FROM Images WHERE author_id = ?""", (USERID,)).fetchall()
            cur.execute("""DELETE FROM Images WHERE author_id = ?""", (USERID,))
            cur.execute("""DELETE FROM Chats WHERE user1_id = ? OR user2_id = ?""", (USERID, USERID))
            for image in images:
                cur.execute("""DELETE FROM Likes WHERE image_id = ?""", (image[0],))
            CON.commit()
            self.close()
        else:
            pass

    def change_theme(self):
        global THEME
        if THEME == 'WHITE':
            THEME = 'BLACK'
        else:
            THEME = "WHITE"
        theme = open('theme.txt', 'wt')
        theme.truncate(0)
        theme.write(THEME)
        self.hide()
        self.widget = Account()
        self.widget.show()


class Entering(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'login.ui', self)
        self.setWindowIcon(QIcon(r'logo.jpg'))
        if THEME == "BLACK":
            self.setStyleSheet('background-color: rgb(0, 0, 0)')
            self.login.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.error.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.label.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.label_2.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.label_3.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.label_5.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')
            self.password.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')

        self.enter.clicked.connect(self.enter_func)
        self.enter.setAutoDefault(True)
        self.error.hide()
        self.reg_btn.clicked.connect(self.reg)

    def reg(self):
        self.hide()
        self.mywidget = Registration()
        self.mywidget.show()

    def enter_func(self):
        global USER_NAME, EMAIL, CON, IMAGE, USERID
        cur = CON.cursor()
        res = cur.execute("""SELECT password, email, image, id FROM Users WHERE user = ?""",
                          (self.login.text(),)).fetchall()
        if res:
            if self.password.text() == res[0][0]:
                USER_NAME = self.login.text()
                EMAIL = res[0][1]
                USERID = res[0][3]
                print(USERID)
                self.home()
            else:
                self.error.show()
                self.error.setText('Неверный пароль!')
                self.password.clear()
        else:
            self.error.setText('Неверный логин!')
            self.error.show()
            self.password.clear()

    def home(self):
        self.hide()
        self.mywidget = MyWidget()
        self.mywidget.show()


class Registration(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'registration.ui', self)
        self.setWindowIcon(QIcon(r'logo.jpg'))
        self.regist_btn.clicked.connect(self.reg_func)
        self.regist_btn.setAutoDefault(True)
        self.image_btn.setIcon(QIcon(r'save.png'))
        self.image_btn.setIconSize(QSize(30, 30))
        self.image_btn.clicked.connect(self.choose_image)
        self.error.hide()
        self.home_btn.setIcon(QIcon(r'back.png'))
        self.home_btn.setIconSize(QSize(40, 40))
        self.home_btn.clicked.connect(self.enter)
        if THEME == "BLACK":
            self.setStyleSheet('background-color: rgb(0, 0, 0)')
            self.label.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.label_2.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')
            self.label_3.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')
            self.label_4.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')
            self.label_5.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')
            self.label_6.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')
            self.login.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.password.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.image.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.password_2.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.email.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.error.setStyleSheet('color: rgb(255, 255, 255);font: 12px "Comfortaa";')

    def choose_image(self):
        global IMAGE
        image = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                            'Картинка jpg (*.jpg);;jpeg (*.jpeg)')[0]
        self.image.setText(image)
        IMAGE = image

    def reg_func(self):
        global CON, USER_NAME, EMAIL, RATING, IMAGE
        login = self.login.text()
        password = self.password.text()
        password_2 = self.password_2.text()
        email = self.email.text()
        check_login = True
        check_email = True
        if login and password_2 and password and email:
            cur = CON.cursor()
            usernames = cur.execute("""SELECT user FROM Users""").fetchall()
            emails = cur.execute("""SELECT email FROM Users""").fetchall()
            if emails:
                for email_bd in emails:
                    if email == email_bd[0]:
                        check_email = False
                        break
            if usernames:
                for username in usernames:
                    if username[0] == login:
                        check_login = False
                        break
            if not check_login:
                self.error.show()
                self.error.setText('Такой логин уже существует!')
            elif not check_email:
                self.error.show()
                self.error.setText('Такой email уже существует!')
            elif password != password_2:
                self.error.show()
                self.error.setText('Пароли не совпадают!')
            else:
                USER_NAME = login
                EMAIL = email
                self.insertBLOB(login, password, email, IMAGE)
                self.home()
        else:
            self.error.show()
            self.error.setText('Поля отмеченные * обязательны для заполнения!')

    def insertBLOB(self, login, password, email, image):
        global USERID, USER_NAME
        sqliteConnection = sqlite3.connect('App.db')
        cursor = sqliteConnection.cursor()
        sqlite_insert_blob_query = """ INSERT INTO Users(user, password, email, image) VALUES (?, ?, ?, ?)"""
        IMAGE = to_binary(image)
        data_tuple = (login, password, email, IMAGE)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        sqliteConnection.commit()
        cur = CON.cursor()
        USERID = cur.execute("""SELECT id FROM Users WHERE user = ?""", (USER_NAME,)).fetchone()[0]
        users = cur.execute("""SELECT id FROM Users WHERE id != ?""", (USERID,)).fetchall()
        for elem in users:
            cur.execute("""INSERT INTO Chats(user1_id, user2_id) VALUES (?, ?)""", (USERID, elem[0]))
            print(elem[0])
        CON.commit()
        cursor.close()

    def home(self):
        self.hide()
        self.mywidget = MyWidget()
        self.mywidget.show()

    def enter(self):
        self.hide()
        self.mywidget = Entering()
        self.mywidget.show()


class Change(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'change.ui', self)
        if THEME == 'BLACK':
            self.setStyleSheet('background-color: rgb(0, 0, 0)')
            self.label.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.label_2.setStyleSheet('color: rgb(255, 255, 255);font: 14px "Comfortaa";')
            self.label_3.setStyleSheet('color: rgb(255, 255, 255);font: 14px "Comfortaa";')
            self.label_4.setStyleSheet('color: rgb(255, 255, 255);font: 14px "Comfortaa";')
            self.login.setStyleSheet(
                'color: rgb(255, 255, 255);font: 14px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.email.setStyleSheet(
                'color: rgb(255, 255, 255);font: 14px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.image.setStyleSheet(
                'color: rgb(255, 255, 255);font: 14px "Comfortaa";border: 1px solid white; border-radius: 20px;')
        self.setWindowIcon(QIcon(r'logo.jpg'))
        self.regist_btn.clicked.connect(self.reg_func)
        self.regist_btn.setAutoDefault(True)
        self.image_btn.setIcon(QIcon(r'save.png'))
        self.image_btn.setIconSize(QSize(30, 30))
        self.image_btn.clicked.connect(self.choose_image)
        self.error.hide()
        self.login.setText(USER_NAME)
        self.email.setText(EMAIL)
        self.home_btn.setIcon(QIcon(r'back.png'))
        self.home_btn.setIconSize(QSize(40, 40))
        self.home_btn.clicked.connect(self.home)

    def choose_image(self):
        global IMAGE
        image = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                            'Картинка jpg (*.jpg);;jpeg (*.jpeg)')[0]
        self.image.setText(image)
        IMAGE = image

    def reg_func(self):
        global CON, USER_NAME, EMAIL, IMAGE
        login = self.login.text()
        email = self.email.text()
        check_login = True
        check_email = True
        cur = CON.cursor()
        usernames = cur.execute("""SELECT user FROM Users WHERE user != ?""",
                                (USER_NAME,)).fetchall()
        emails = cur.execute("""SELECT email FROM Users WHERE user != ?""", (USER_NAME,)).fetchall()
        for email_bd in emails:
            if email == email_bd[0]:
                check_email = False
                break
        for username in usernames:
            if username[0] == login:
                check_login = False
                break
        if login and email:
            if not check_login:
                self.error.show()
                self.error.setText('Такой логин уже существует!')
            elif not check_email:
                self.error.show()
                self.error.setText('Такой email уже существует!')
            else:
                EMAIL = email
                if bool(self.image.text()):
                    cur.execute("""UPDATE Users SET image = ? WHERE user = ?""",
                                (to_binary(IMAGE), USER_NAME))
                user = USER_NAME
                USER_NAME = login
                cur.execute("""UPDATE Users SET user = ? WHERE user = ?""", (USER_NAME, user))
                cur.execute("""UPDATE Users SET email = ? WHERE user = ?""", (EMAIL, USER_NAME))
                CON.commit()
                self.home()
        else:
            self.error.show()
            self.error.setText('Все поля должны быть заполнены!')

    def home(self):
        self.hide()
        self.mywidget = Account()
        self.mywidget.show()

    def closeEvent(self, event):
        self.home()
        event.accept()


class Chats(QMainWindow):
    def __init__(self):
        global USERID
        super().__init__()
        self.scroll = QScrollArea()
        self.setWindowIcon(QIcon(r'logo.jpg'))
        if THEME == 'BLACK':
            self.setStyleSheet('background-color: rgb(0, 0, 0)')
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        cur = CON.cursor()
        res = cur.execute("""SELECT * FROM CHATS WHERE user1_id = ? OR user2_id = ?""",
                          (USERID, USERID)).fetchall()
        self.object = {}
        for elem in res:
            name = elem[1] if elem[1] != USERID else elem[2]
            write_name = cur.execute("""SELECT user FROM Users WHERE id = ?""", (name,)).fetchone()
            self.object[elem[0]] = QPushButton(str(write_name[0]), self)
            self.object[elem[0]].clicked.connect(self.open_chat)
            self.object[elem[0]].setStyleSheet("""font: 18pt "Comfortaa";
background-color: rgb(3, 135, 201);
color: rgb(255, 255, 255);
border: 1px solid rgb(3, 135, 201);
border-radius: 20px;""")
            self.vbox.addWidget(self.object[elem[0]], 2)

        self.vbox.addStretch(1)
        self.widget.setLayout(self.vbox)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 500, 300)
        self.setWindowTitle('Чаты')
        self.show()

        return

    def home(self):
        self.hide()
        self.mywidget = MyWidget()
        self.mywidget.show()

    def open_chat(self):
        global CHATID
        for key, value in self.object.items():
            if value == self.sender():
                CHATID = key
                self.open()

    def open(self):
        self.chat = Chat()
        self.chat.show()
        self.close()


class Chat(QMainWindow):
    def __init__(self):
        global USER_NAME, CHATID
        super().__init__()
        self.setWindowIcon(QIcon(r'logo.jpg'))
        uic.loadUi(r'chat.ui', self)
        if THEME == 'BLACK':
            self.setStyleSheet('background-color: rgb(0, 0, 0)')
            self.listWidget.setStyleSheet('color: rgb(255, 255, 255);font: 75 10pt "Comfortaa";')
            self.lineEdit.setStyleSheet('font: 75 10pt "Comfortaa";color: rgb(255, 255, 255);')
        self.home_btn.setIcon(QIcon(r'back.png'))
        self.home_btn.setIconSize(QSize(40, 40))
        self.home_btn.clicked.connect(self.home)
        cur = CON.cursor()
        info = cur.execute(
            """SELECT * FROM (SELECT user, message, msg_id, chat_id FROM Messages JOIN Users ON Messages.user_id = Users.id WHERE chat_id = ? ORDER BY Messages.msg_id DESC LIMIT 30)  ORDER BY msg_id ASC;""",
            (CHATID,))
        for elem in info:
            name = 'Я' if elem[0] == USER_NAME else elem[0]
            self.listWidget.addItem('{} : {}'.format(name, elem[1]))
        self.send_btn.clicked.connect(self.send)

    def home(self):
        self.hide()
        self.chat = Chats()
        self.chat.show()
        self.close()

    def send(self):
        global USERID
        text = self.lineEdit.text()
        if bool(text):
            self.listWidget.addItem('Я : {}'.format(text))
            cur = CON.cursor()
            cur.execute("""INSERT INTO Messages(user_id, message, chat_id) VALUES(?,?,?)""",
                        (USERID, text, CHATID))
            CON.commit()
            self.lineEdit.clear()


class Add_Picture(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(r'logo.jpg'))
        uic.loadUi(r'add_picture.ui', self)
        if THEME == 'BLACK':
            self.setStyleSheet('background-color: rgb(0, 0, 0)')
            self.label_3.setStyleSheet('color: rgb(255, 255, 255);font: 20pt "Comfortaa";')
            self.label.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.label_2.setStyleSheet('color: rgb(255, 255, 255);font: 18pt "Comfortaa";')
            self.commentedit.setStyleSheet(
                'color: rgb(255, 255, 255);font: 14px "Comfortaa";border: 1px solid white; border-radius: 20px;')
            self.imageline.setStyleSheet(
                'color: rgb(255, 255, 255);font: 12px "Comfortaa";border: 1px solid white; border-radius: 20px;')
        self.image_button.clicked.connect(self.add_image)
        self.post_btn.clicked.connect(self.post)
        self.image_button.setIcon(QIcon(r'save.png'))
        self.image_button.setIconSize(QSize(30, 30))

    def add_image(self):
        self.image = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                                 'Картинка jpg (*.jpg);;jpeg (*.jpeg)')[0]
        self.imageline.setText(self.image)

    def post(self):
        global USERID
        if not bool(self.imageline.text()):
            self.error.setText('Добавьте изображение')
        if not bool(self.commentedit.text()):
            self.error.setText('Добавьте комментарий')
        else:
            sqliteConnection = sqlite3.connect('App.db')
            cursor = sqliteConnection.cursor()
            sqlite_insert_blob_query = """ INSERT INTO Images(author_id, image, text) VALUES (?, ?, ?)"""
            image = to_binary(self.image)
            data_tuple = (USERID, image, self.commentedit.text())
            cursor.execute(sqlite_insert_blob_query, data_tuple)
            sqliteConnection.commit()
            cursor.close()
            self.hide()
            self.home = MyWidget()
            self.home.show()
            self.close()

    def home(self):
        self.main = MyWidget()
        self.main.show()

    def closeEvent(self, event):
        self.home = MyWidget()
        self.home.show()
        event.accept()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Entering()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
