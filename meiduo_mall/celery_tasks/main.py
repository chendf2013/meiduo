from celery import Celery

# 为celery使用django配置文件进行设置
import os


if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# 创建celery对象(并给celery起名字)
celery_app = Celery("meiduo")

# 导入配置文件
celery_app.config_from_object("celery_tasks.config")

# 注册任务(主动去搜索任务)传进来的是个列表，可以传递多个任务
celery_app.autodiscover_tasks(["celery_tasks.sms", "celery_tasks.email", "celery_tasks.html"])

    # 开启celery的方法命令(多进程，几个核，几个进程)
    # celery -A 应用路径 （.包路径） worker -l info
    # celery -A celery_tasks.main worker -l info
