from database import db
from flask.ext.security import UserMixin, RoleMixin, SQLAlchemyUserDatastore

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)

    def __repr__(self):
        return '<models.User[email=%s]>' % self.email


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class SomeStuff(db.Model):
    __tablename__ = 'somestuff'
    id = db.Column(db.Integer, primary_key=True)
    data1 = db.Column(db.Integer)
    data2 = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User, lazy='joined', join_depth=1, viewonly=True)

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
    whelp_date = db.Column(db.Date)
    desc = db.Column(db.String)
    registered_name = db.Column(db.String)
    registration = db.relationship('Registration', secondary="dog_registration", backref="dog")
    sex = db.Column('sexes',db.Enum("male", "female",name="sexes"))
    # sire_id = db.Column(db.Integer, db.ForeignKey('dog.id',use_alter=True,name="sire_fk"))
    title = db.relationship('Title', secondary="dog_title", backref=db.backref('dog',lazy='dynamic'))
    thumbnail = db.Column(db.String)
    # dam = db.relationship('Dog', primaryjoin = ('dog.dam_id == dog.id'),lazy="joined",post_update=True)
    # sire = db.relationship('Dog', primaryjoin = ('dog.sire_id == dog.id'),lazy="joined",post_update=True)
