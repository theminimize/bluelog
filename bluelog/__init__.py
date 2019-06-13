# -*- coding: utf-8 -*-
"""
工厂函数一般在程序包的构造文件中创建
在OOP中工厂(factory)通常是指创建其他对象的对象，通常是一个返回其他类的对象的函数和方法
使用工厂函数可以在任何地方创建程序实例，借助工厂函数，可以分离拓展的初始化操作
工厂函数接收配置名作为参数，返回创建好的程序实例
初始化拓展类，但不传入程序实例，拓展类实例化由extensions.py脚本进行操作
"""
import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.extensions import bootstrap, db, login_manager, csrf, ckeditor, mail, moment, toolbar, migrate
from bluelog.models import Admin, Post, Category, Comment, Link
from bluelog.settings import config

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))   # 返回脚本文件路径


def create_app(config_name=None):   # 定义工厂函数,设置配置名为空
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')  # 从FLASK_CONFIG环境变量获取配置名参数，设置默认值为development

    app = Flask('bluelog')  # 创建程序实例app
    app.config.from_object(config[config_name])     # 从settings.py,配置类字典获取相应配置类

    # 组织工厂函数
    register_logging(app)   # 注册日志处理器
    register_extensions(app)    # 注册拓展（拓展初始化）
    register_blueprints(app)    # 注册蓝本(蓝图)
    register_commands(app)  # 注册自定义shell命令
    register_errors(app)    # 注册错误处理函数
    register_shell_context(app)  # 注册shell上下文处理函数
    register_template_context(app)  # 注册模板上下文处理函数
    register_request_handlers(app)  # 不知道是啥...
    return app  # 返回程序实例


def register_logging(app):  # 注册日志处理器函数(略)
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/bluelog.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=['ADMIN_EMAIL'],
        subject='Bluelog Application Error',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    if not app.debug:
        app.logger.addHandler(mail_handler)
        app.logger.addHandler(file_handler)


def register_extensions(app):   # 注册拓展初始化
    # init_app()方法为各类中所定义的方法，用于初始化及相关配置
    # init_app()方法用于支持分离拓展的实例化和初始化操作
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):   # 注册蓝图
    # 蓝图使用Flask.register_blueprint()方法注册，传入参数为:创建的蓝图对象-from bluelog.blueprints import blog_bp引入
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app):    # 注册shell上下文
    @app.shell_context_processor    # shell上下文处理装饰器
    def make_shell_context():   # 设置上下文
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)
        # 等同于return {'db':db, 'Admin':Admin, 'Post':Post, 'Category':Category, 'Comment':Comment}

def register_template_context(app):  # 注册模板上下文
    @app.context_processor  # 上下文装饰器
    def make_template_context():    # 设置模板上下文
        admin = Admin.query.first()  # query.first()返回查询的第一条记录
        categories = Category.query.order_by(Category.name).all()   # 按Category.name排序,返回包含所有查询记录的列表
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:   # Flask_LOGIN模块, 判断登录状态
            # filter_by过滤器，使用指定规则(参数)，返回新的查询对象,的个数(.count)
            unread_comments = Comment.query.filter_by(reviewed=False).count()   # 未读评论
        else:
            unread_comments = None
        return dict(
            admin=admin, categories=categories,
            links=links, unread_comments=unread_comments)   # 返回字典


def register_errors(app):   # 注册自定义错误函数
    @app.errorhandler(400)  # 监听捕获异常装饰器
    def bad_request(e):
        return render_template('errors/400.html'), 400  # 渲染自定义错误信息模板及错误代码:400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)    # 当CSRF验证失败时，将引发CSRFError异常
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):  # 注册自定义命令
    @app.cli.command()  # 添加命令行接口
    @click.option('--drop', is_flag=True, help='Create after drop.')    # 使用click提供的option装饰器添加自定义数量支持
    def initdb(drop):   # 初始化数据库,传入drop参数
        """初始化数据库"""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,   # hide_input隐藏输入内容
                  confirmation_prompt=True, help='The password used to login.')     #confirmation_prompt设置二次确认输入
    def init(username, password):   # 博客初始化,传入用户名和密码
        """创建BLUELOG，个性化博客"""

        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()  # 从数据库中查找管理员记录
        if admin is not None:   # 如果数据库中已经有管理员记录就更新用户名和密码
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)    # 调用Admin模型类中的set_password()方法，生成password
        else:   # 没有管理员记录则创建新的管理员记录
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)   # 将新创建对象添加到数据库会话

        category = Category.query.first()
        if category is None:    # 如果没有分类则创建默认分类
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()  # 调用session.commit()，将改动提交到数据库
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """创建模拟数据"""
        from bluelog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')


def register_request_handlers(app):  # 注册请求捕获函数
    @app.after_request  # 请求钩子,未抛出异常，则在每个请求结束后运行后续代码，after_request钩子应用场景为进行数据库操作如更新，删除
    def query_profiler(response):
        for q in get_debug_queries():
            if q.duration >= app.config['BLUELOG_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: Duration: %fs\n Context: %s\nQuery: %s\n '
                    % (q.duration, q.context, q.statement)
                )
        return response
