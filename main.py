import requests.cookies
from flask import *
from connectors.BinanceConnection import *
from connectors.BitmexConnection import *
from database import WorkspaceData
import datetime
from flask_session import Session
from strategy_execution import Execute_strategy
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

binance = None
bitmex = None

@app.route('/')
def login():  #put application's code here
    return render_template('login.html', retry=False, errorType='none')


@app.route('/validate_login', methods=['POST', 'GET'])
def validate_login():
    if request.method == 'POST':
        if 'login' in request.form:
            user_name = request.form.get('user')
            password = request.form.get('pass')
            db = WorkspaceData()
            data = db.get('login', user_name)
            for s in data:
                #print(s['username'])
                if user_name == s['username'] and password == s['password']:
                    keys = db.get('keys', user_name)
                    for k in keys:
                        global binance
                        binance = BinanceConnection(str(k[1]), str(k[2]), True, True)
                        global bitmex
                        bitmex = BitmexConnection(str(k[3]), str(k[4]), True)
                    session['username'] = user_name
                    return redirect('/home')
            #print('name is ',user_name)
            #print('password is ', password)
            return render_template('login.html', retry=True, errorType='login')
        elif 'signup' in request.form:
            user_name = request.form.get('user')
            password1 = request.form.get('pass1')
            password2 = request.form.get('pass2')
            email = request.form.get('email')
            print(password1)
            print(password2)
            if str(password1) == str(password2) and len(password1) != 0:
                try:
                    db = WorkspaceData()
                    db.add('login', [(user_name, password1, email)])
                    return render_template('login.html', retry=False, errorType='none')
                except:
                    return render_template('login.html', retry=True, errorType='signup_already_exists')
            else:
                return render_template('login.html', retry=True, errorType='signup')


@app.route('/home', methods=['POST', 'GET'])
def home():
    return render_template('home.html', app_session=session)


@app.route('/logging_component')
def logging():
    return render_template('logging_component.html', binance=binance, bitmex=bitmex, bid_asks=0)


@app.route('/strategies_component')
def strategies():
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h']
    if binance is None or bitmex is None:
        return redirect('/missing_keys')
    db = WorkspaceData()
    data = db.get('strategies', session['username'])
    #for d in data:
    #    print(d[0]+" "+d[1]+" "+d[2]+" "+d[3]+" "+d[4]+" "+d[5]+" "+d[6]+" "+d[7]+" ")
    table_data = {'user': [], 'strategy_type': [], 'element': [], 'timeframe': [], 'balance_pct': [], 'take_profit': [], 'stop_loss': [], 'activate': []}
    for d in data:
        table_data['user'].append(d[0])
        table_data['strategy_type'].append(d[1])
        table_data['element'].append(d[2])
        table_data['timeframe'].append(d[4])
        table_data['balance_pct'].append(d[5])
        table_data['take_profit'].append(d[6])
        table_data['stop_loss'].append(d[7])
        table_data['activate'].append(d[8])
        #binance.add_log(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+' : '+d[2])
    print(table_data)
    table_length = len(table_data['user'])
    print(table_length)
    return render_template('strategy_component.html',timeframes=timeframes,binance=binance,bitmex=bitmex, table_data = table_data, table_length = table_length)


@app.route('/save_strategies', methods=['POST', 'GET'])
def save_strategies():
    if request.method == 'POST':
        strategy_type = request.form.getlist('strategy_type')
        elements = request.form.getlist('elements')
        balance_pcd = request.form.getlist('balance_pcd')
        timeframe = request.form.getlist('timeframe')
        tp = request.form.getlist('tp')
        sl = request.form.getlist('sl')
        activate = request.form.getlist('activate_btn')
        element = []
        exchange = []
        for i in range(len(elements)):
            x = elements[i].split('_')
            element.append(x[0])
            exchange.append(x[1])

        print(strategy_type)
        print(element)
        print(exchange)
        print(timeframe)
        print(balance_pcd)
        print(tp)
        print(sl)
        print(activate)
        db = WorkspaceData()
        data = []
        for i in range(1, len(strategy_type)):
            data.append((session['username'], strategy_type[i], element[i], exchange[i], timeframe[i], balance_pcd[i], tp[i], sl[i], activate[i]))
        db.save('strategies', data, session['username'])
        e = Execute_strategy(binance, bitmex, session)
        return redirect('/strategies_component')


@app.route('/watchlist_component', methods=['POST', 'GET'])
def watchlist():
    if binance is None or bitmex is None:
        return redirect('/missing_keys')
    db = WorkspaceData()
    wl_data = db.get('watchlist', session['username'])
    bid_asks1 = []
    for row in wl_data:
        if row[2] == 'Binance':
            bid_ask = dict()
            bid_ask['symbol'] = row[1]
            bid_ask['exchange'] = 'Binance'
            bid_ask['data'] = dict()
            bid_ask['data'] = binance.get_bid_ask(binance.contracts[row[1]])
            bid_asks1.append(bid_ask)
        elif row[2] == 'Bitmex':
            bid_ask = dict()
            bid_ask['symbol'] = row[1]
            bid_ask['exchange'] = 'Bitmex'
            bid_ask['data'] = dict()

            precision = bitmex.contracts[row[1]].price_decimals
            prices = bitmex.prices[row[1]]
            bid_price = -1
            ask_price = -1
            if prices['bid'] is not None:
                bid_price = "{0:.{prec}f}".format(prices['bid'], prec=precision)
            if prices['ask'] is not None:
                ask_price = "{0:.{prec}f}".format(prices['ask'], prec=precision)
            data = {'bid': bid_price, 'ask': ask_price}
            bid_ask['data'] = data
            bid_asks1.append(bid_ask)

    if request.method == 'POST':
        binance_elements = request.form['binance_symbols'].split('_')
        binance_elements = [element for element in binance_elements if element != '']
        for row in wl_data:
            if row[2] == 'Binance':
                binance_elements.append(row[1])
        binance_elements = set(binance_elements)
        binance_elements = list(binance_elements)
        #print(binance_elements)
        bid_asks = []
        for element in binance_elements:
            bid_ask = dict()
            bid_ask['symbol'] = element
            bid_ask['exchange'] = 'Binance'
            bid_ask['data'] = dict()
            bid_ask['data'] = binance.get_bid_ask(binance.contracts[element])
            bid_asks.append(bid_ask)

        bitmex_elements = request.form['bitmex_symbols'].split('_')
        bitmex_elements = [element for element in bitmex_elements if element != '']
        for row in wl_data:
            if row[2] == 'Bitmex':
                bitmex_elements.append(row[1])
        bitmex_elements = set(bitmex_elements)
        bitmex_elements = list(bitmex_elements)
        #print(bitmex_elements)
        for element in bitmex_elements:
            bid_ask = dict()
            bid_ask['symbol'] = element
            bid_ask['exchange'] = 'Bitmex'
            bid_ask['data'] = dict()

            precision = bitmex.contracts[element].price_decimals
            prices = bitmex.prices[element]
            bid_price = -1
            ask_price = -1
            if prices['bid'] is not None:
                bid_price = "{0:.{prec}f}".format(prices['bid'], prec=precision)
            if prices['ask'] is not None:
                ask_price = "{0:.{prec}f}".format(prices['ask'], prec=precision)
            data = {'bid': bid_price, 'ask': ask_price}
            bid_ask['data'] = data
            bid_asks.append(bid_ask)
        #print(bid_asks)
        #print("1111:"+request.form['bitmex_elements'])
        return render_template('watchlist_component.html', binance=binance, bitmex=bitmex, bid_asks=bid_asks,
                               binance_elements=request.form['binance_symbols'], bitmex_elements=request.form['bitmex_symbols'])
    else:
        return render_template('watchlist_component.html', binance=binance, bitmex=bitmex, bid_asks=bid_asks1)


@app.route('/save_watchlist', methods=['POST', 'GET'])
def save_watchlist():
    if request.method == 'POST':
        symbol = request.form.getlist('symbol')
        exchange = request.form.getlist('exchange')
        print(symbol)
        print(exchange)
        db = WorkspaceData()
        data = []
        for s, e in zip(symbol, exchange):
            data.append((session['username'], s, e))
        print(data)
        db.save('watchlist', data, session['username'])
    return redirect('/watchlist_component')


@app.route('/trades_component')
def trades_component():
    if binance is None or bitmex is None:
        return redirect('/missing_keys')
    return render_template('trades_component.html', client=binance)


@app.route('/profile')
def profile():
    db = WorkspaceData()
    login_data = db.get('login', session['username'])
    keys_data = db.get('keys', session['username'])
    keys = dict()
    for k in keys_data:
        keys['binance_private_key'] = k[1]
        keys['binance_public_key'] = k[2]
        keys['bitmex_private_key'] = k[3]
        keys['bitmex_public_key'] = k[4]
    #print(keys)
    return render_template('profile.html', login_data=login_data, keys_data=keys)


@app.route('/save_profile', methods=['GET', 'POST'])
def save_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        print(username)
        print(password)
        print(email)
    return redirect('/profile')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/missing_keys')
def missing_keys():
    return render_template('missing_keys.html')


if __name__ == '__main__':
    #binance = BinanceConnection('d5fd694f19a8c4feeec259e7d74e244d69f1bedf8af4a49c9387e2ea20a57433','b874a84f38efff2941fe2fcd86e83056a670d581e8187bd9641f263f5acfda26', True, True)

    #bitmex = BitmexConnection("YaTEaHBxKCB4t9XRCIlWd2Nq", "FB-_2AK9FwGhBiAZQd59GhfHI2GCsffpq_aCKkfrUjRTELeX", True)
    app.run(debug=True)
