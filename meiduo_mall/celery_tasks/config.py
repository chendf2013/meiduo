# 储存任务队列的redis
result_backend = 'redis://127.0.0.1:6379/15'
# 后端是保存储存结果的，若没有执行返回结果，就不用配置
broker_url = 'redis://127.0.0.1:6379/14'