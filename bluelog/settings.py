# -*- coding: utf-8 -*-
"""
配置类文件,使用单个配置文件使用Python类组织多个不同类别配置
包含基本配置类(BaseConfig):父类,测试配置类(TestingConfig),开发配置类(DevelopmentConfig),生产配置类(ProductionConfig)：子类
配置文件底部，创建存储配置名称与对应配置类的字典，用于创建程序实例时通过配置名称，获取对应配置类
配置名称必须全大写形式，小写变量不被读取
"""
import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))   # 用于获取数据库路径,__file__为特殊变量

# SQLite URI compatible
WIN = sys.platform.startswith('win')    # 判定是系统环境为windows还是其他，选取不同URI前缀
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')     # os.getenv()获取环境变量,Flask使用这个密钥来对cookies和别的东西进行签名

    DEBUG_TB_INTERCEPT_REDIRECTS = False    # Flask-debugger参数,是否拦截重定向

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # SQLAlchemy警告信息
    SQLALCHEMY_RECORD_QUERIES = True    # 显式的禁用或启用查询记录

    CKEDITOR_ENABLE_CSRF = True     # 开启CSRF保护
    CKEDITOR_FILE_UPLOADER = 'admin.upload_image'   # 使用admin.upload_image函数上传图片

    MAIL_SERVER = os.getenv('MAIL_SERVER')  # 获取用于发送邮件的SMTP服务器
    MAIL_PORT = 465     # 发信端口
    MAIL_USE_SSL = True     # 是否使用SSL/TLS
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')      # 发送服务器的用户名
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')      # 发送服务器的的密码
    MAIL_DEFAULT_SENDER = ('Bluelog Admin', MAIL_USERNAME)      # 默认发信人

    BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL')
    BLUELOG_POST_PER_PAGE = 10      # 每个页面文章个数
    BLUELOG_MANAGE_POST_PER_PAGE = 15   # 管理文章页面文章显示个数
    BLUELOG_COMMENT_PER_PAGE = 15   # 每页评论数

    BLUELOG_THEMES = {'perfect_blue': 'Perfect Blue', 'black_swan': 'Black Swan'}   # 主题字典(主题名称与CSS文件名对应：显示名称)
    BLUELOG_SLOW_QUERY_THRESHOLD = 1    #

    BLUELOG_UPLOAD_PATH = os.path.join(basedir, 'uploads')  # 上传路径
    BLUELOG_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']    # 允许上传的图片格式


class DevelopmentConfig(BaseConfig):    # 开发配置类
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')     # 设置数据库URI，数据库文件名为data-dev.db


class TestingConfig(BaseConfig):    # 测试配置类
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):     # 生产配置类
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))

# 配置config映射字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
