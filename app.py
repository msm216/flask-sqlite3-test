import os
import pandas as pd

from datetime import datetime, timezone, timedelta

from flask import Flask
from flask import request
from flask import render_template, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date
from sqlalchemy import create_engine, cast
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename


#from models import User, Group


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/path/to/upload'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
db = SQLAlchemy(app)


#engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
#Session = sessionmaker(bind=engine)
#session = Session()



class Group(db.Model):
    __tablename__ = 'group_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    first_register = db.Column(Date, nullable=True)
    last_register = db.Column(Date, nullable=True)
    # 反向关联，lazy='dynamic' 使得反向关系被访问时返回一个对象而不是列表
    users = db.relationship('User', backref='user_group', lazy=True)

    def __repr__(self):
        return f'<Group {self.name}>'

class User(db.Model):
    __tablename__ = 'user_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    group_id = db.Column(db.Integer, db.ForeignKey('group_table.id'), default=0)
    #group = db.relationship('Group', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'<User {self.name}>'


@app.route('/')
def index():
    # 获取所有用户和组
    users = User.query.all()
    groups = Group.query.all()
    # 更新每个组的 first_register 和 last_register
    for group in groups:
        group_users = [user for user in users if user.group_id == group.id]
        if group_users:
            group.first_register = min(user.registered_on for user in group_users)
            group.last_register = max(user.registered_on for user in group_users)
        else:
            group.first_register = None
            group.last_register = None
    db.session.commit()

    ###### filter user by id ######
    user_min_id = request.args.get('min_id', default=1, type=int)
    user_max_id = request.args.get('max_id', default=999999, type=int)
    print(f"Selecting user ID between {user_min_id} and {user_max_id}.")
    user_id_query = User.query.filter(User.id.between(user_min_id, user_max_id))

    ###### filter user by group ######
    group_ids = request.args.getlist('group_select', type=int)    # 根据 name 属性选择
    print(f"Selecting user in group: {group_ids}")
    if group_ids:
        user_id_query = user_id_query.filter(User.group_id.in_(group_ids))
    filtered_users = user_id_query.all()

    ###### filter group by date ######
    group_start_date = request.args.get('start_date', default='2000-01-01', type=str)
    group_end_date = request.args.get('end_date', default=datetime.today().strftime('%Y-%m-%d'), type=str)
    print(f"Selecting group created from {group_start_date} to {group_end_date}.")
    filtered_groups = Group.query.filter(Group.created_on.between(
        datetime.strptime(group_start_date, '%Y-%m-%d').date(), 
        datetime.strptime(group_end_date, '%Y-%m-%d').date() + timedelta(days=1))).all()
    
    return render_template('index.html', 
                           users=filtered_users, 
                           groups=filtered_groups,
                           group_ids=group_ids)

######## 处理 User ########

# 确保日期格式为 <class 'datetime.datetime'>
def date_for_sqlite(meta_date:str) -> datetime:
    if meta_date == '':
        new_date = datetime.now(timezone.utc)
    else:
        new_date = datetime.strptime(meta_date, '%Y-%m-%d')
    return new_date

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
    print(f"Adding new group named: '{new_name}' created on {new_date}")
    # 判断group名是否已存在
    existing_group = Group.query.filter_by(name=new_name).first()
    if existing_group:
        return jsonify({'success': False, 'message': 'Group name already exists'}), 400
    new_group = Group(name=new_name, created_on=date_for_sqlite(new_date))
    db.session.add(new_group)
    db.session.commit()
    return jsonify(success=True), 200

@app.route('/delete_group/<int:id>', methods=['DELETE'])
def delete_group(id):
    group = Group.query.get(id)
    #group = session.get(Group, id)
    db.session.delete(group)
    db.session.commit()
    return jsonify(success=True)

@app.route('/edit_group/<int:id>', methods=['POST'])
def edit_group(id):
    data = request.json
    new_name = data['name']
    new_date = data['created_on']
    print(f"Modifying group {id} to name: '{new_name}' created on {new_date}")
    # 判断是否存在其他名称相同的实例
    existing_group = Group.query.filter_by(name=new_name).first()
    if existing_group and existing_group.id != id:
        return jsonify(success=False, message="Group name already exists"), 400
    # 正常修改对象实例
    group = Group.query.get(id)
    #group = session.get(Group, id)
    if group:
        group.name = new_name
        group.created_on = date_for_sqlite(new_date)
        db.session.commit()
        return jsonify(success=True), 200
    # id错误
    return jsonify(success=False, message="Group not found"), 404

######## 处理文件上传 ########

# 验证文件扩展名
def allowed_file(filename:str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx'}

# 根据上传的数据 DataFrame 更新表格
def update_groups_from_dataframe(df:pd.DataFrame) -> None:
    # 逐条遍历 DataFrame
    for _, row in df.iterrows():
        group_id = row['id']
        group_name = row['name']
        created_on = row['created_on']
        #first_register = row.get('first_register')
        #last_register = row.get('last_register')

        # 尝试根据 id 获取数据库中已有实例
        group = Group.query.get(group_id)
        if group is None:
            # 不存在同 id 实例则添加
            group = Group(id=group_id, name=group_name, created_on=created_on)
            print(f"Add new instance: {group}")
            db.session.add(group)
        else:
            # 存在同 id 实例则更新部分属性
            print(f"Update instance: {group}")
            group.name = group_name
            group.created_on = created_on
            #group.first_register = first_register
            #group.last_register = last_register
            pass
        db.session.commit()

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查请求中是否包含文件，如果不存在，显示错误信息并重定向回上传页面
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # 如果文件名为空，显示错误信息并重定向回上传页面
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    # 验证文件后缀
    if file and allowed_file(file.filename):
        # 确保上传的文件名是安全的，并移除任何可能导致安全问题的字符
        filename = secure_filename(file.filename)
        # 构建文件路径
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 处理文件
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath, parse_dates=['created_on'])
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filepath, parse_dates=['created_on'])
        else:
            flash('Unsupported file format')
            return redirect(request.url)

        # 将文件内容更新到数据库
        update_groups_from_dataframe(df)
        flash('File successfully uploaded and processed')
        return redirect(url_for('index'))

    flash('File type not allowed')
    return redirect(request.url)



if __name__ == '__main__':

    app.run(debug=True)