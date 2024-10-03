from stations.extensions import db


class User(db.Model):
    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80, collation='NOCASE'), unique=True, nullable=False)
    email = db.Column(db.String(120, collation='NOCASE'), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    is_connected = db.Column(db.Boolean)
    is_active = db.Column(db.Boolean)
    roles = db.relationship('Role', backref='user', lazy=True)
    data = db.relationship('Data', backref='user', lazy=True)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Data(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    project = db.Column(db.String(500))
    projectpro = db.Column(db.String(500))
    cint = db.Column(db.String(500))
    comp = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
