from datetime import datetime, timezone

from . import db


class Group(db.Model):

    __tablename__ = 'group_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    first_register = db.Column(db.DateTime, nullable=True)
    last_register = db.Column(db.DateTime, nullable=True)
    # 反向关联，lazy='dynamic' 使得反向关系被访问时返回一个对象而不是列表
    users = db.relationship('User', backref='user_group', lazy=True)

    def __repr__(self):
        return f'<Group: {self.name}>'

class User(db.Model):

    __tablename__ = 'user_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    group_id = db.Column(db.Integer, db.ForeignKey('group_table.id'), default=0)
    #group = db.relationship('Group', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'<User: {self.name}>'