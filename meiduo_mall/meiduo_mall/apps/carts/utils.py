import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """登陆后将cookie中的合并到redis中"""

    # 获取登录的user_id
    user_id = user.id
    # print(user)

    # 从cookie中获取购物车信息
    # cookie_cart_dict = request.COOKIES.get("cart")
    cookie_cart_dict = request.COOKIES.get('cart')
    # print(cookie_cart_dict)

    if not cookie_cart_dict:
        return response

    cart_dict = pickle.loads(base64.b64decode(cookie_cart_dict.encode()))
    # print(cart_dict)

    # 获取redis中的信息
    redis_cnn = get_redis_connection("cart")
    pl = redis_cnn.pipeline()

    # 用户中的购物车不一定有内容，因此不需要去获取，而是直接创建或者覆盖
    # redis_cart_dict=pl.hget("cart_%s"%user_id)
    # redis_cart_list=pl.lrange("selected_%s"%user_id)

    # 保存到redis中
    for sku_id, selected_count_dict in cart_dict.items():
        pl.hset("cart_%s" % user_id, sku_id, selected_count_dict["count"])
        if selected_count_dict.get("selected"):
            pl.sadd('cart_selected_%s' % user.id, sku_id)
        else:
            pl.srem('cart_selected_%s' % user.id, sku_id)

    # 管道执行
    pl.execute()

    # 将cookie中的信息删除
    response.delete_cookie("cart")
    # 返回响应
    return response
    # 寻找调用时机（登录与QQ登录）
    # 登录是drf内置的登录视图函数，需要重写
