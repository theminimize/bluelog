# -*- coding: utf-8 -*-
"""
extensions.py文件用于拓展类的实例化
将全局拓展对象db,bootstrap等放置到工厂函数之外如：extensions.py，这样工厂函数才有全局拓展对象使用
"""
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate

# 拓展类实例化
bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
mail = Mail()
moment = Moment()
toolbar = DebugToolbarExtension()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):     # 用户加载函数，接收用户ID为参数，返回对应的用户对象
    from bluelog.models import Admin
    user = Admin.query.get(int(user_id))    # 如果用户已登录则返回Admin类实例
    return user  # 返回对应用户对象


login_manager.login_view = 'auth.login'
# login_manager.login_message = 'Your custom message'
login_manager.login_message_category = 'warning'
