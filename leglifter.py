import flask
import flask.ext.sqlalchemy
import flask.ext.restless

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = flask.ext.sqlalchemy.SQLAlchemy(app)

# Create your Flask-SQLALchemy models as usual but with the following two
# (reasonable) restrictions:
#   1. They must have a primary key column of type sqlalchemy.Integer or
#      type sqlalchemy.Unicode.
#   2. They must have an __init__ method which accepts keyword arguments for
#      all columns (the constructor in flask.ext.sqlalchemy.SQLAlchemy.Model
#      supplies such a method, so you don't need to declare a new one).

dog_clearance = db.Table('dog_clearance',
    db.Column('dog_id',db.Integer, db.ForeignKey('dog.id')),
    db.Column('clearance_id',db.Integer, db.ForeignKey('clearance.id'))
)

dog_registration = db.Table('dog_registration',
    db.Column('dog_id',db.Integer, db.ForeignKey('dog.id')),
    db.Column('registration_id',db.Integer, db.ForeignKey('registration.id'))
)

dog_title = db.Table('dog_title',
    db.Column('dog_id',db.Integer, db.ForeignKey('dog.id')),
    db.Column('title_id',db.Integer, db.ForeignKey('title.id'))
)

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.Unicode)
#     password = db.Column(db.Unicode)
#     email = db.Column(db.String(128))

class Body(db.Model):
    __tablename__ = 'body'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, unique=True)
    abrv = db.Column(db.String(64), index=True, unique=False)
    url  = db.Column(db.String(64), index=True, unique=False)

class Clearance(db.Model):
    __tablename__ = 'clearance'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body_id = db.Column(db.Integer, db.ForeignKey('body.id',use_alter=True,name="body_fk"))
    body = db.relationship(Body, uselist=False,post_update=True)
    test = db.Column(db.String)
    info = db.Column(db.String)

class Registration(db.Model):
    __tablename__ = 'registration'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body_id = db.Column(db.Integer, db.ForeignKey('body.id',use_alter=True,name="body_fk"))
    body = db.relationship(Body, uselist=False,post_update=True)
    registration_text = db.Column(db.String)

class Title(db.Model):
    __tablename__ = 'title'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body_id = db.Column(db.Integer, db.ForeignKey('body.id',use_alter=True,name="body_fk"))
    body = db.relationship(Body,uselist=False,post_update=True)
    name = db.Column(db.String)
    abrv = db.Column(db.String)
    desc = db.Column(db.String)
    fix = db.Column("fix",db.Enum("pre", "suf", name="fix"))

class Dog(db.Model):
    __tablename__ = 'dog'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    altered = db.Column(db.Boolean)
    bg_image = db.Column(db.String)
    call_name = db.Column(db.String)
    clearance = db.relationship('Clearance', secondary=dog_clearance, backref=db.backref('dog',lazy='dynamic'))
    # dam_id = db.Column(db.Integer, db.ForeignKey('dog.id',use_alter=True,name="dams_fk"))
    date_of_birth = db.Column(db.Date)
    desc = db.Column(db.String)
    registered_name = db.Column(db.String)
    registration = db.relationship('Registration', secondary="dog_registration", backref="dog")
    sex = db.Column('sexes',db.Enum("male", "female",name="sexes"))
    # sire_id = db.Column(db.Integer, db.ForeignKey('dog.id',use_alter=True,name="sire_fk"))
    title = db.relationship('Title', secondary="dog_title", backref=db.backref('dog',lazy='dynamic'))
    thumbnail = db.Column(db.String)
    # dam = db.relationship('Dog', primaryjoin = ('dog.dam_id == dog.id'),lazy="joined",post_update=True)
    # sire = db.relationship('Dog', primaryjoin = ('dog.sire_id == dog.id'),lazy="joined",post_update=True)


# Create the database tables.
db.create_all()

# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
url_prefix='/v1'
manager.create_api(Body, methods=['GET', 'POST', 'DELETE'],url_prefix=url_prefix)
manager.create_api(Clearance, methods=['GET', 'POST', 'DELETE'],url_prefix=url_prefix)
manager.create_api(Registration, methods=['GET', 'POST', 'DELETE'],url_prefix=url_prefix)
manager.create_api(Title, methods=['GET', 'POST', 'DELETE'],url_prefix=url_prefix)
manager.create_api(Dog, methods=['GET', 'POST', 'DELETE'],url_prefix=url_prefix)

# start the flask loop
app.run()
