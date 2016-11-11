from bottle import run, get, static_file, redirect


@get('/')
def index():
    from smart_qq_bot.app import bot
    tpl = '<h1>If QR Code is shown, please scan!</h1>' \
          '<h2>Login Out Dated: {login_out_dated} </h2>' \
          '<img src="/qr_code.jpg" alt="qr_code"/>' \
          '<h1>click <a href="/re-login">here</a> to re-login</h1>'
    return tpl.format(
        login_out_dated=bot.login_out_dated
    )


@get('/qr_code.jpg')
def qr_code():
    from smart_qq_bot.config import QR_CODE_FNAME
    return static_file(QR_CODE_FNAME, root=".")


@get('/re-login')
def re_login():
    from smart_qq_bot.app import bot
    bot.login(no_gui=True)
    return redirect("/")


def run_server(host="0.0.0.0", port=8888):
    run(host=host, port=port)
