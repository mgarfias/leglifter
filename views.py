# Views  ======================================================================
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/mypage')
@login_required
def mypage():
    return render_template('mypage.html')


@app.route('/logout')
def log_out():
    logout_user()
    return redirect(request.args.get('next') or '/')

@app.route('/enqueue_registration')
@login_required
def sqs_enqueue():
    return "Fart"
