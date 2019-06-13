# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app


# 判断安全链接，防止形成开放重定向漏洞
def is_safe_url(target):
    # request.host_url获取程序内主机URL
    ref_url = urlparse(request.host_url)
    # urljoin()函数将目标URL转换为绝对URL
    test_url = urlparse(urljoin(request.host_url, target))
    # 最后对目标URL的URL模式和主机地址进行验证，确保只返回属于程序内部的URL
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# 重定向回上一个页面
def redirect_back(default='blog.index', **kwargs):
    # 手动加入包含当前页面的URL的查询参数 next,request.referrer获取referrer的值,referrer记录用户所在原站点URL
    # 首先获取next参数，如果为空则常识获取referer,如果仍为空则重定向到默认的blog.index视图
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


# 给允许上传的文件加上“.”
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['BLUELOG_ALLOWED_IMAGE_EXTENSIONS']
