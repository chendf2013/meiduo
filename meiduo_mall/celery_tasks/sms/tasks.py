from celery_tasks.main import celery_app
from celery_tasks.sms import constants
from celery_tasks.sms.yuntongxun.sms import CCP


# 起名字
@celery_app.task(name="send_sms_code")
# 可以传递函数名字与函数的参数(因此可以将可变参数传递进来)
def send_sms_code(mobile,sms_code):
    """
    发送短信验证码的celery任务
    :param mobiel 手机号码
    :param sms_code 手机验证码
    :return None
    """
    # 发送短信验证码
    ccp = CCP()
    time = constants.SMS_CODE_REDIS_EXPIRES / 60
    ccp.send_template_sms(mobile, (sms_code, time), constants.SMS_CODE_TEMP_ID)