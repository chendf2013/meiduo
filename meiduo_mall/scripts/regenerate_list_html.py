#!/usr/bin/env python


import sys

from django.conf import settings
from django.template import loader


sys.path.insert(0, '../')
sys.path.insert(0, '../meiduo_mall/apps')


import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

 # 让django进行初始化设置
import django
django.setup()
from goods.models import *
from goods.utils import get_categories
def generate_static_list_search_html():
    """
    生成静态的商品列表页html文件
    """
    # 商品分类菜单
    categories = get_categories()

    # 渲染模板，生成静态html文件
    context = {
        'categories': categories,
    }

    template = loader.get_template('list.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'list.html')
    with open(file_path, 'w') as f:
        f.write(html_text)



if __name__ == '__main__':
    generate_static_list_search_html()