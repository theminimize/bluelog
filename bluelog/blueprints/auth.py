# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from bluelog.forms import LoginForm
from bluelog.models import Admin
from bluelog.utils import redirect_back

# 创建蓝图实例
auth_bp = Blueprint('auth', __name__)


# 登录页面
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 如果已登录，重定向回到主页
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    # 实例化登录表单类
    form = LoginForm()
    # 表单提交并验证通过
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        # 从数据库中查询出Admin对象，判断username的值，并使用Admin类中的validate_password()方法验证密码
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                # 通过验证就调用login_user()方法登录用户，传入admin对象和remember字段的值作为参数
                login_user(admin, remember)
                flash('欢迎回来！', 'info')
                return redirect_back()  # 重定向回上一个页面
            flash('用户名或密码错误。', 'warning')
        else:
            flash('还没有注册账户！', 'warning')
    return render_template('auth/login.html', form=form)


# 注销页面
@auth_bp.route('/logout')
@login_required  # 视图保护装饰器
def logout():
    # 调用Flask-Login提供的logout_user()函数
    logout_user()
    flash('注销成功。', 'info')
    return redirect_back()
