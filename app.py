from flask import *

app = Flask(__name__)


@app.route('/')
def home():  # put application's code here
    return render_template('home.html')



@app.route('/test')
def test():
    data = ['harsha', 'vardhan', 'rajender', 'anuradha']
    return render_template('names.html', names=data)


if __name__ == '__main__':
    app.run()
