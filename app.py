from datetime import datetime, timezone, timedelta

from flask import Flask
from flask import request
from flask import render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import cast, Date

#from models import User, Group


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
#Session = sessionmaker(bind=engine)
#session = Session()



# 确保日期格式为 <class 'datetime.datetime'>
def date_for_sqlite(meta_date:str) -> datetime:
    if meta_date == '':
        new_date = datetime.now(timezone.utc)
    else:
        new_date = datetime.strptime(meta_date, '%Y-%m-%d')
    return new_date


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), default=0)
    # 反向关系?
    group = db.relationship('Group', backref=db.backref('users', lazy=True))


@app.route('/')
def index():
    print("Selecting:")
    ###### filter user with id ######
    user_min_id = request.args.get('min_id', default=1, type=int)
    user_max_id = request.args.get('max_id', default=999999, type=int)
    print(f"user_min_id: {user_min_id} ({type(user_min_id)})")
    print(f"user_max_id: {user_max_id} ({type(user_max_id)})")
    filtered_users = User.query.filter(User.id.between(user_min_id, user_max_id)).all()
    ###### filter group with date ######
    group_start_date = request.args.get('start_date', default='2000-01-01', type=str)
    group_end_date = request.args.get('end_date', default=datetime.today().strftime('%Y-%m-%d'), type=str)
    print(f"group_start_date: {group_start_date} ({type(group_start_date)})")
    print(f"group_end_date: {group_end_date} ({type(group_end_date)})")
    filtered_groups = Group.query.filter(Group.created_on.between(
        datetime.strptime(group_start_date, '%Y-%m-%d').date(), 
        datetime.strptime(group_end_date, '%Y-%m-%d').date()+timedelta(days=1))).all()
    
    return render_template('index.html', users=filtered_users, groups=filtered_groups)

######## 处理 User ########

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    new_name = data['name']
    new_date = data['registered_on']
    group_id = data['group_id'] if data['group_id'] != 'None' else None
    new_user = User(name=new_name, registered_on=date_for_sqlite(new_date), group_id=group_id)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(success=True)

@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify(success=True)

@app.route('/edit_user/<int:id>', methods=['POST'])
def edit_user(id):
    user = User.query.get(id)
    data = request.json
    user.name = data['name']
    user.group_id = data['group_id']
    db.session.commit()
    return jsonify(success=True)

######## 处理 Group ########

@app.route('/add_group', methods=['POST'])
def add_group():
    data = request.json
    new_name = data['name']
    new_date = data['created_on']
    print("Adding:")
    print(new_name, 'of type', type(new_name))
    print(new_date, 'of type', type(new_date))
    new_group = Group(name=new_name, created_on=date_for_sqlite(new_date))
    db.session.add(new_group)
    db.session.commit()
    return jsonify(success=True)

@app.route('/delete_group/<int:id>', methods=['DELETE'])
def delete_group(id):
    group = Group.query.get(id)
    #group = session.get(Group, id)
    db.session.delete(group)
    db.session.commit()
    return jsonify(success=True)

@app.route('/edit_group/<int:id>', methods=['POST'])
def edit_group(id):
    group = Group.query.get(id)
    #group = session.get(Group, id)
    data = request.json
    new_name = data['name']
    new_date = data['created_on']
    print(new_name, 'of type', type(new_name))
    print(new_date, 'of type', type(new_date))
    group.name = new_name
    group.created_on = date_for_sqlite(new_date)
    db.session.commit()
    return jsonify(success=True)


if __name__ == '__main__':

    app.run(debug=True)