import sys
import sqlite3
import datetime

from PyQt5.QtWidgets import QPushButton, QMainWindow, QApplication, QLabel, QScrollArea, QVBoxLayout,\
    QWidget, QHBoxLayout, QTextBrowser, QDialog
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from urllib import request
from PyQt5.QtCore import QDate
from PIL import Image


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('cinema 1.0.ui', self)
        self.edit_but = dict()
        self.tick_but = dict()
        self.del_btd = dict()
        self.film_window()
        self.search_btn.clicked.connect(self.change)
        self.btn_add.clicked.connect(self.edit)

    def film_window(self):
        time = self.comboBox.currentText()
        print(time)

        date = self.dateEdit.text()
        print(date)

    # ДБ запрос
        con = sqlite3.connect("cinema.db")
        cur = con.cursor()

        a = f"""SELECT id FROM films
            WHERE id IN (SELECT id_film FROM sessions WHERE time = '{time + ':00'}' AND date = '{date}')"""
        print(a)
        id_films = cur.execute(a).fetchall()

    # Создание layouts для Scroll_area
        self.scroll = QScrollArea(self)
        self.scr_layout = QVBoxLayout()
        ws = QWidget()


    #Создание виджетов в цикле
        for i in id_films:
            inf_layout = QHBoxLayout()

        #Отображение картинки
            url = cur.execute(f"""SELECT urlWeb FROM films
                    WHERE id = ?""", (i[0],)).fetchall()

            label_film = QLabel(self)
            inf_layout.addWidget(label_film)
            print(*url[0])
            img = Image.open(request.urlopen(*url[0]))
            img.save(f'tmp.jpg')
            pixmap = QPixmap(f'tmp.jpg')
            pixmap = pixmap.scaledToWidth(128)
            label_film.setPixmap(pixmap)

        # Информация о фильме
            title = cur.execute(f"""SELECT title FROM films
                                    WHERE id = ?""", (i[0],)).fetchall()
            genre = cur.execute(f"""SELECT name FROM genres
                                    WHERE id = (SELECT genre FROM films WHERE id = ?)""", (i[0],)).fetchall()
            year = cur.execute(f"""SELECT year FROM films
                                        WHERE id = ?""", (i[0],)).fetchall()
            duration = cur.execute(f"""SELECT duration FROM films
                                            WHERE id = ?""", (i[0],)).fetchall()
            description = cur.execute(f"""SELECT shortDescription FROM films
                                            WHERE id = ?""", (i[0],)).fetchall()
            country = cur.execute(f"""SELECT country FROM films
                                            WHERE id = ?""", (i[0],)).fetchall()

            text_inf = QTextBrowser(self)
            text_inf.setText(f'{title[0][0]}\n\nЖанр: {genre[0][0]}\nГод: {year[0][0]}\n'
                             f'Длительность: {duration[0][0]} минут\nСтрана: {country[0][0]}'
                             f'\n\n{description[0][0]}')
            inf_layout.addWidget(text_inf)

            self.scr_layout.addLayout(inf_layout)

        # Кнопка редактирования
            btn = QPushButton('Редактировать сеанс', self)
            self.edit_but[btn] = i[0]
            btn.resize(100, 100)
            inf_layout.addWidget(btn)
            btn.clicked.connect(self.edit)

        # Кнопка покупки билета
            btn_t = QPushButton('Купить билет', self)
            inf_layout.addWidget(btn_t)
            self.tick_but[btn_t] = i[0]
            btn_t.clicked.connect(self.buy_ticket)

        # Кнопка удаления сеанса
            del_btn = QPushButton('x', self)
            inf_layout.addWidget(del_btn)
            self.del_btd[del_btn] = i[0]
            del_btn.setStyleSheet('background-color: rgb(255, 0, 4);')
            del_btn.clicked.connect(self.dele)

        ws.setLayout(self.scr_layout)
        self.scroll.show()
        self.scroll.setWidget(ws)
        self.scroll.setGeometry(0, 135, 1072, 680)

    def change(self):
        try:
            self.film_window()
        except Exception as e:
            print(e)

    def edit(self):
        try:
            if self.sender().text() == 'Редактировать сеанс':
                self.edit_w = EditWindow(self.edit_but[self.sender()])
            else:
                self.edit_w = EditWindow(0)
            self.edit_w.show()
        except Exception as e:
            print(e)

    def buy_ticket(self):
        self.tic_wind = TicketWindow(self.tick_but[self.sender()])
        self.tic_wind.show()

    def dele(self):
        con = sqlite3.connect("cinema.db")
        cur = con.cursor()
        id_film = self.del_btd[self.sender()]
        print(id_film)
        data, time = cur.execute("""SELECT data AND time sessions where id_film = ?""", (id_film, )).fetchall()
        print(data[0][0], time[0][0])
        cur.execute("""DELETE from sessions where id = ?""", (1, )).fetchall()


class EditWindow(QWidget):
    def __init__(self, film):
        super().__init__()
        uic.loadUi('edit.ui', self)
        self.film = film
        now = str(datetime.datetime.now())

        date = QDate(int(now[:4]), int(now[5:7]), int(now[8:10]))
        print(date, now)
        self.calendar.setSelectedDate(date)
        self.btn.clicked.connect(self.apply)
        self.run()

    def run(self):
        self.con = sqlite3.connect("cinema.db")
        cur = self.con.cursor()
        title = cur.execute("""SELECT title FROM films""").fetchall()
        title.sort()
        for i in title:
            self.box_films.addItem(i[0])

        if self.film != 0:
            film_name = cur.execute("""SELECT title FROM films WHERE id = ?""", (self.film,)).fetchall()

            dat = cur.execute("""SELECT date FROM sessions WHERE id_film = ?""", (self.film,)).fetchall()
            date = QDate(int(dat[0][0][6:]), int(dat[0][0][3:5]), int(dat[0][0][:2]))

            time = cur.execute("""SELECT time FROM sessions WHERE id_film = ?""", (self.film,)).fetchall()

            price = cur.execute("""SELECT price FROM sessions WHERE id_film = ?""", (self.film,)).fetchall()

            id_room = cur.execute("""SELECT name FROM rooms WHERE id = (SELECT id_room FROM sessions 
            WHERE id_film = ?)""", (self.film,)).fetchall()

            self.box_rooms.setCurrentText(id_room[0][0])
            self.box_time.setCurrentText(time[0][0][:-3])
            self.box_films.setCurrentText(film_name[0][0])
            self.line_price.setText(str(price[0][0]))
            self.calendar.setSelectedDate(date)

    def apply(self):
        cur = self.con.cursor()

        c_date = self.calendar.selectedDate().toPyDate()

        d = '.'.join((str(c_date).split('-')))
        d = d[8:] + d[4:8] + d[:4]

        film = self.box_films.currentText()
        room = self.box_rooms.currentText()
        id_room = cur.execute("""SELECT id FROM rooms WHERE name = ?""", (room,)).fetchall()
        time = self.box_time.currentText()
        id_film = cur.execute("""SELECT id FROM films WHERE title = ?""", (film,)).fetchall()
        price = self.line_price.text()
        m_id = cur.execute("""SELECT id FROM sessions""").fetchall()
        m_id.sort(reverse=True)
        id_session = int(m_id[0][0])

        print(id_film[0][0], d, time + ':00', int(price), 0, int(id_room[0][0]), sep='\n')
        if self.film != 0:
            try:
                cur.execute(f"""UPDATE sessions
    SET id_film = ?, time = ?, id_room = ?, price = ?, date = ?
    WHERE id_film = ?""", (id_film[0][0], time + ':00', id_room[0][0], price, d, self.film)).fetchall()
                self.con.commit()
                self.close()
            except Exception as e:
                print(e)
        else:
            # Добавление в базу данных
            try:
                cur.execute(f"""INSERT INTO sessions(id, id_film, date, time, price, amount, id_room) 
        VALUES({id_session + 1}, {id_film[0][0]}, '{d}', '{time + ':00'}', {price}, 0, {id_room[0][0]})""").fetchall()
                self.con.commit()
                self.close()
            except Exception as e:
                print(e)


class TicketWindow(QDialog):
    def __init__(self, id_film):
        super().__init__()
        uic.loadUi('tickets.ui', self)
        self.con = sqlite3.connect("cinema.db")
        self.id_film = id_film

        self.lineEdit.textChanged.connect(self.amount_t)
        self.pushButton_2.clicked.connect(self.add_one)
        self.initt()

        self.pushButton.clicked.connect(self.complete)

    def initt(self):
        cur = self.con.cursor()
        self.amount = cur.execute(f"""SELECT amount FROM sessions WHERE id_film = ?""", (self.id_film, )).fetchall()
        self.amount = ' ' * (3 - len(str(self.amount[0][0]))) + str(self.amount[0][0])
        print(self.amount)
        self.label_4.setText(str(self.amount))

        room_name = cur.execute(f"""SELECT name FROM rooms WHERE id IN (SELECT id_room 
FROM sessions WHERE id_film = ?)""", (self.id_film, )).fetchall()
        self.label_2.setText(room_name[0][0])
        self.sits = cur.execute(f"""SELECT count FROM rooms WHERE name = ?""", (room_name[0][0], )).fetchall()
        self.price = cur.execute(f"""SELECT price FROM sessions WHERE id_film = ?""", (self.id_film,)).fetchall()
        self.label.setText('/' + str(self.sits[0][0]))
        self.label_5.setText('0₽')

    def amount_t(self):
        self.add_tickets = self.lineEdit.text()
        if self.add_tickets != '':
            if int(self.add_tickets) + int(self.amount) <= self.sits[0][0]:
                self.label_4.setText(str(int(self.amount) + int(self.add_tickets)))
                self.label_5.setText(str(int(self.lineEdit.text()) * self.price[0][0]) + '₽')
        else:
            self.initt()

    def add_one(self):
        if self.lineEdit.text() != '':
            if int(self.add_tickets) + int(self.amount) <= self.sits[0][0]:
                    self.lineEdit.setText(str(int(self.lineEdit.text()) + 1))
            else:
                self.lineEdit.setText('1')

    def complete(self):
        cur = self.con.cursor()
        cur.execute(f"""UPDATE sessions
            SET amount = ? WHERE id_film = ?""", (int(self.label_4.text()), self.id_film)).fetchall()
        self.con.commit()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())