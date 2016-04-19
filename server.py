from flask import render_template, jsonify, request, redirect
from flask.ext.security import Security, logout_user, login_required
from flask.ext.security.utils import encrypt_password, verify_password
from flask.ext.restless import APIManager
from flask_jwt import JWT, jwt_required, current_identity
from flask_boto_sqs import FlaskBotoSQS
from database import db
from application import app
from models import User, user_datastore, Body, Clearance, Registration, Title, Dog, Member
from admin import init_admin
import user_stuff

# Setup Flask-Security  =======================================================
security = Security(app, user_datastore)

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

# really should make this generic so it works for all queue types
@app.route(app.config['URL_PREFIX'] + '/queue_registration', methods=['GET', 'POST'])
@login_required
def queue_registration():
    q_name = app.config['FLASK_BOTO_SQS']['queues']['registration']
    try:
        q = flask_boto_sqs.sqs.get_queue_by_name(QueueName=q_name)
        resp = q.send_message('What a lovely day!')
        return resp.get('MessageId')
    except:
        return "Error no queue exists: {}".format(q_name)

@app.route(app.config['URL_PREFIX'] + '/user', methods=['GET'])
@jwt_required()
def get_user():
    resp = {
        'email': current_identity.email,
        'active': current_identity.active,
        'confirmed_at': current_identity.confirmed_at,
        'last_login_at': current_identity.last_login_at,
        'current_login_at': current_identity.current_login_at,
        'last_login_ip': current_identity.last_login_ip,
        'current_login_ip': current_identity.current_login_ip
    }
    return jsonify(resp), 200

# membership stuffs ===========================================================
@app.route(app.config['URL_PREFIX'] + '/member/valid', methods=['GET'])
@jwt_required()
def valid_member():
    # for now
    #if username == "mike@garfias.org":
    #    return True
    if current_identity['active'] == "true":
        return True
    return False

# JWT Token authentication  ===================================================
def authenticate(username, password):
    user = user_datastore.find_user(email=username)
    if user and username == user.email and verify_password(password, user.password):
        return user
    return None

def load_user(payload):
    user = user_datastore.find_user(id=payload['identity'])
    return user

jwt = JWT(app, authenticate, load_user)

# Flask-Restless API  =========================================================
@jwt_required()
def auth_func(**kw):
    pass

apimanager = APIManager(app, flask_sqlalchemy_db=db)
#apimanager.create_api(SomeStuff,
#    methods=['GET', 'POST', 'DELETE', 'PUT'],
#    url_prefix=app.config['URL_PREFIX'],
#    collection_name='free_stuff',
#    include_columns=['id', 'data1', 'data2', 'user_id'])

# apimanager.create_api(SomeStuff,
#     methods=['GET', 'POST', 'DELETE', 'PUT'],
#     url_prefix=app.config['URL_PREFIX'],
#     preprocessors=dict(GET_SINGLE=[auth_func], GET_MANY=[auth_func]),
#     collection_name='protected_stuff',
#     include_columns=['id', 'data1', 'data2', 'user_id'])

apimanager.create_api(Body,
    methods=['GET', 'POST', 'DELETE'],
    url_prefix=app.config['URL_PREFIX'],
    collection_name='bodies')

apimanager.create_api(Clearance,
    methods=['GET', 'POST', 'DELETE'],
    url_prefix=app.config['URL_PREFIX'])

apimanager.create_api(Registration,
    methods=['GET', 'POST', 'DELETE'],
    url_prefix=app.config['URL_PREFIX'])

apimanager.create_api(Title,
    methods=['GET', 'POST', 'DELETE'],
    url_prefix=app.config['URL_PREFIX'])

apimanager.create_api(Dog,
    methods=['GET', 'POST', 'DELETE'],
    url_prefix=app.config['URL_PREFIX'])

apimanager.create_api(Member,
    methods=['GET', 'POST', 'DELETE'],
    url_prefix=app.config['URL_PREFIX'])



# Setup Admin  ================================================================
init_admin()


# Bootstrap  ==================================================================
def create_test_models():
    user_datastore.create_user(email='test', password=encrypt_password('test'))
    user_datastore.create_user(email='mike@garfias.org', password=encrypt_password('mike'))
    db.session.commit()

@app.before_first_request
def bootstrap_app():
    if not app.config['TESTING']:
        if db.session.query(User).count() == 0:
            create_test_models()

# Start server  ===============================================================
if __name__ == '__main__':
    db.init_app(app)
    flask_boto_sqs = FlaskBotoSQS(app)
    with app.app_context():
        db.create_all()
    app.run()
