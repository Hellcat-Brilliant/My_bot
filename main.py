from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import requests as wr
import json
import datetime
import sqlite3


class cats():
    def __init__(self):
        self.cur = None
        self.con = None
        self.init_db()
        self.flask = Flask(__name__)
        self.set_routes()
        # Разкомментировать, что бы запустить локально
        self.flask.run(port=8080, host='127.0.0.1')
        #run_with_ngrok(self.flask)
        #self.flask.run()

    def set_routes(self):
        @self.flask.route('/')
        @self.flask.route('/index')
        @self.flask.route('/cats')
        def index():
            return render_template('index.html', href=self.get_image())

        @self.flask.route('/register', methods=['POST', 'GET'])
        def register():
            if request.method == 'GET':
                return render_template('register.html')
            if request.method == 'POST':
                self.new_user(request.form['login'], request.form['pass'])
                return "Вы успешно зарегистрировались!" +\
                    "<script>location='/login';</script>"

        @self.flask.route('/login', methods=['POST', 'GET'])
        def login():
            if request.method == 'GET':
                return render_template('login.html')
            if request.method == 'POST':
                return self.user_auth(
                    request.form['login'],
                    request.form['pass']
                    )

    def init_db(self):
        self.con = sqlite3.connect("db.db", check_same_thread=False)
        self.cur = self.con.cursor()

    def user_auth(self, login, passw):
        result = self.cur.execute("""
            SELECT * FROM users WHERE
            name = '""" + login + """' and
            pass = '""" + passw + """'
            ORDER BY ID DESC LIMIT 1
        """).fetchall()
        if len(result) > 0:
            result = result[0]
            return "Привет, " + str(result[1]) + "!<br>" +\
                "Ваша дата регистрации: " + str(result[3])
        return "Ошибка входа"

    def new_user(self, login, passw):
        current_time = datetime.datetime.now().strftime("%d.%m.%Y %I:%M:%S")
        self.cur.execute("""INSERT INTO users (name, pass, date)
                    VALUES ('{}', '{}', '{}') """.format(
            login,
            passw,
            current_time)
        )

        self.con.commit()

    def get_image(self):
        response = wr.get("https://api.thecatapi.com/v1/images/search")
        return json.loads(response.text)[0]['url']


if __name__ == '__main__':
    app = cats()
