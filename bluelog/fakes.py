# -*- coding: utf-8 -*-
"""
为方便编写前台和后台功能，我们在建立数据库模型之后就编写生成虚拟数据的函数
"""
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from bluelog import db
from bluelog.models import Admin, Category, Post, Comment, Link

fake = Faker()   # 实例化Faker()类


def fake_admin():   # 虚拟管理员信息
    admin = Admin(
        username='admin',
        blog_title='Bluelog',
        blog_sub_title="No, I'm the real thing.",
        name='Mima Kirigoe',
        about='Um, l, Mima Kirigoe, had a fun time as a member of CHAM...'
    )   # 实例化Admin对象，并赋初值
    admin.set_password('helloflask')    # 调用admin的set_password()方法，生成密码，这里默认密码为helloflask
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):  # 虚拟分类，默认10个分类
    category = Category(name='Default')  # 添加一个名为Default的默认分类，为创建文章时默认的分类
    db.session.add(category)

    for i in range(count):  # 循环生成随机分类
        category = Category(name=fake.word())
        db.session.add(category)
        try:    # 由于Category分类名不能重复，因此需要采用try-except捕获异常，db.session.rollback()回滚操作
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):   # 虚拟文章
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),  # 随机分配到某个分类
            timestamp=fake.date_time_this_year()
        )

        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):   # 虚拟评论
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,  # 虚拟评论，默认已审核
            post=Post.query.get(random.randint(1, Post.query.count()))  # 随机放入文章
        )
        db.session.add(comment)

    salt = int(count * 0.1)     # 生成未审核的评论
    for i in range(salt):
        # unreviewed comments
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # 管理员评论
        comment = Comment(
            author='Mima Kirigoe',
            email='mima@example.com',
            site='example.com',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    # 生成回复
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()


def fake_links():   # 设置链接
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    linkedin = Link(name='LinkedIn', url='#')
    google = Link(name='Google+', url='#')
    db.session.add_all([twitter, facebook, linkedin, google])
    db.session.commit()
