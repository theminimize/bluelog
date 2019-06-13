# -*- coding: utf-8 -*-
"""
如果博客内容有大量固定信息，则可以将其存储在自定义配置文件中或是写死在模板中，若信息设置交给用户则会用到数据库模型，进行信息规范
对于密码一般是存储其hash值，而不存储密码本身，验证密码时通过特定方法装换成hash值进行比对
对于评论和回复，需要在Comment中添加外键指向自身，以此得到层级关系，每个评论对象包含多个子评论
在reply和comment中由于在同一模型中，SQLAlchemy无法分辨关系两侧，所以需要通过remote_side参数定义关系哪一个是远程侧，哪一个为本地侧
以此定义为多对一关系，即多回复对应一个评论
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from bluelog.extensions import db


class Admin(db.Model, UserMixin):   # 创建管理员模型，存储管理员资料和博客资料
    id = db.Column(db.Integer, primary_key=True)    # 创建字段属性，主键primary_key
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))   # password的hash散列值，不存储密码只存储hash值
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):   # 定义设置密码的函数，通过用户输入的password，用对应加密方法，返回对应password_hash值
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):  # 验证密码
        return check_password_hash(self.password_hash, password)


class Category(db.Model):   # 文章分类数据库模型
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)    # 分类名不允许重复，参数unique=True

    posts = db.relationship('Post', back_populates='category')  # 这里分类category与post是一对多关系,posts为集合关系属性

    def delete(self):   # 删除指定分类
        default_category = Category.query.get(1)    # 获取默认分类记录，query.get()传入主键做参数，返回对应主键记录
        posts = self.posts[:]   # [:]截取列表全部内容
        for post in posts:
            post.category = default_category    # 为该分类下文章记录重新指定到默认分类
        db.session.delete(self)  # 删除分类记录
        db.session.commit()


class Post(db.Model):   # 文章模型类
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 设置时间戳，index=True建立索引
    can_comment = db.Column(db.Boolean, default=True)   # 用于评论开关功能，存储是否评论的布尔值

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))   # 将category.id设置为外键，与分类建立关系
    category = db.relationship('Category', back_populates='posts')      # 标量关系属性category

    # comments集合关系属性, cascade设置级联操作，即文章删除，评论随之删除
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')


class Comment(db.Model):    # 评论模型类
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)   # 判断是否为管理员评论，管理员评论无需审核
    reviewed = db.Column(db.Boolean, default=False)     # 存储评论是否通过审核
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # 将comment.id设置为外键与Comment本身建立关系,得到层级关系
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))   # 将post.id设置为外键与Post建立关系

    post = db.relationship('Post', back_populates='comments')   # back_populates定义反向引用
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')    # 回复设置级联操作
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])    # 将id字段定义为远程侧
    # Same with:
    # replies = db.relationship('Comment', backref=db.backref('replied', remote_side=[id])
    # cascade='all,delete-orphan')


class Link(db.Model):   # 其他网站链接类模型
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))
