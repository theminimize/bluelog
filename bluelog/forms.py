# -*- coding: utf-8 -*-
"""
    表单用于用户交互，采集用户数据
    Bluelog涉及到登录表单，文章表单，分类表单，评论表单，博客设置表单
    flask-wtf将表单数据解析，CSRF保护，文件上传等功能与Flask集成
    文章表单中分类下拉列表的选项必须是包含两个元素元组的列表,元组分别包含选项值和选项标签,
    使用分类id作为选项值,分类名称作为选项标签,通过迭代Category.query.order_by(Category.name).all()返回分类记录实现
"""
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
# 导入form字段
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
# 导入form验证器
from wtforms.validators import DataRequired, Email, Length, Optional, URL

from bluelog.models import Category


# 登录表单,继承FlaskForm基类
class LoginForm(FlaskForm):
    # 文本字段StringField对应HTML<input type="text">,DataRequired()验证数据是否有效,Length验证输入值长度
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    # 密码字段PasswordField对应HTML<input type="password">,会使用黑色圆点表示密码
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    # 复选框字段BooleanField对应HTML<input type="checkbox">
    remember = BooleanField('Remember me')
    # 提交按钮SubmitField对应HTML<input type="submit">
    submit = SubmitField('Log in')


# 设置表单
class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 70)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title', validators=[DataRequired(), Length(1, 100)])
    # 富文本编辑框字段CKEditorField,需要从flask_ckeditor导入,对应HTML为<textarea></textarea>
    about = CKEditorField('About Page', validators=[DataRequired()])
    # 未更改表单提交按钮名称,默认值为Submit
    submit = SubmitField()


# 文章表单
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    # 下拉列表SelectField对应HTML<select><option></option></select>,选择值默认为字符串类型,coerce关键字指定为整型,默认选项值为1
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

    # 文章表单中分类下拉列表的选项必须是包含两个元素元组的列表,元组分别包含选项值和选项标签,
    # 使用分类id作为选项值,分类名称作为选项标签,通过迭代Category.query.order_by(Category.name).all()返回分类记录实现
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


# 分类表单
class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    # 表单自定义行内验证器，用于验证分类名重复
    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')


# 评论表单
class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    # TextAreaField多行文本字段对应HTML<textarea></textarea>
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()


# 管理员评论表单,继承自评论表单,由于不需要填写作者，邮箱和站点因此采用HiddenField类进行重新定义,代表隐藏字段对应HTML<input type="hidden">
class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


# 添加链接表单
class LinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField()
