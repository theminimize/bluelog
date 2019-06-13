# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
# 多线程模块
from threading import Thread

from flask import url_for, current_app
from flask_mail import Message

from bluelog.extensions import mail


# 异步发送邮件
def _send_async_mail(app, message):
    # 使用with调用app.app_context()手动激活程序上下文
    with app.app_context():
        mail.send(message)


# 发送邮件函数
def send_mail(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    # 创建新线程实例
    thr = Thread(target=_send_async_mail, args=[app, message])
    # 开始此线程
    thr.start()
    return thr


def send_new_comment_email(post):
    # 由于邮件内容简单,直接在发信函数中写出正文内容
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    send_mail(subject='New comment', to=current_app.config['BLUELOG_EMAIL'],
              html='<p>New comment in post <i>%s</i>, click the link below to check:</p>'
                   '<p><a href="%s">%s</a></P>'
                   '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                   % (post.title, post_url, post_url))


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    send_mail(subject='New reply', to=comment.email,
              html='<p>New reply for the comment you left in post <i>%s</i>, click the link below to check: </p>'
                   '<p><a href="%s">%s</a></p>'
                   '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                   % (comment.post.title, post_url, post_url))
