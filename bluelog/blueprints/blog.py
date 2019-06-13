# -*- coding: utf-8 -*-
"""
    :使用蓝本不仅仅是对视图函数的分类，而是将程序某一部分的所有操作组织在一起。
    :蓝本实例以及一系列注册在蓝本实例上的操作的集合被称为一个蓝本
    :使用蓝本可以将程序模块化，蓝本下的所有路由设置不同的URL前缀或子域名
    :蓝本一般在子包中创建，使用包管理蓝本允许你设置蓝本独有的静态文件和模板，并在蓝本内对各类函数分模块存储
"""
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from flask_login import current_user

from bluelog.emails import send_new_comment_email, send_new_reply_email
from bluelog.extensions import db
from bluelog.forms import CommentForm, AdminCommentForm
from bluelog.models import Post, Category, Comment
from bluelog.utils import redirect_back

# 用flask下的Blueprint创建蓝本实例
blog_bp = Blueprint('blog', __name__)


# 博客默认页面
@blog_bp.route('/')
# 获取分页记录
def index():
    page = request.args.get('page', 1, type=int)    # 从查询字符串获取当前页数，默认值为1
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']  # 从配置变量获取每页文章数量
    # 调用查询方法paginate()会返回一个Pagination类实例，它包含分页信息，我们称为分页对象,order_by()以文章时间排序
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)   # 分页对象
    posts = pagination.items    # 当前页数的记录列表，pagination对象调用items属性以列表形式返回对应页数的记录
    return render_template('blog/index.html', pagination=pagination, posts=posts)   # 模板渲染


# 关于页面
@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


# 分类页面显示
@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)   # get_or_404()方法查询指定id的记录
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']  # 从配置变量获取每页文章数
    # with_parent(category)查询方法传入分类对象，最终筛选出属于该分类的所有文章记录(返回查询对象)
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items    # pagination对象调用items属性以列表形式返回对应页数的记录
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


# 文章正文显示
@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)   # get_or_404()方法查询指定id的记录
    page = request.args.get('page', 1, type=int)    # 查询参数获取page页码
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']   # 从配置变量获取每页评论数
    # with_parent()传入模型类实例作为参数,返回和这个实例相关的对象,filter_by()使用指定规则过滤记录,order_by()根据制定规则排序
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(
        page, per_page)  # 分页对象，这里的with_parent(post)方法获取文章所属的评论
    comments = pagination.items  # pagination对象调用items属性以列表形式返回对应页数的记录

    # 判断当前用户认证状态，渲染对应评论表单
    if current_user.is_authenticated:
        # 通过认证，实例化管理员评论表单类
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        # 未通过认证，实例化匿名用户评论表单类
        form = CommentForm()
        from_admin = False
        reviewed = False

    # 如果表单提交并通过验证
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        # 实例化Comment类,传入相应参数
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed)
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)  # 获取回复记录
            comment.replied = replied_comment   # 恢复记录赋值给comment.replied
            send_new_reply_email(replied_comment)   # 发送新回复提醒邮件
        db.session.add(comment)  # 添加到数据库会话
        db.session.commit()  # 提交到数据库
        if current_user.is_authenticated:  # 管理员的回复
            flash('Comment published.', 'success')
        else:   # 匿名用户发布评论提示
            flash('Thanks, your comment will be published after reviewed.', 'info')
            send_new_comment_email(post)  # 发送审核提醒邮件
        return redirect(url_for('.show_post', post_id=post_id))  # 重定向到.show_post
    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


# 显示回复评论标记
@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)  # 返回comment_id对应comment记录
    # 判断当前是否支持评论
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    # URL片段#comment-form用来将页面焦点调到评论表单位置
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')

# 更换网站主题
@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    # make_response()方法生成一个重定向响应
    response = make_response(redirect_back())
    # 对响应对象调用set_cookies设置cookie，将主题的名称保存在名为theme的cookie中，我们使用max_age参数将cookie的过期时间设置为30天
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response
