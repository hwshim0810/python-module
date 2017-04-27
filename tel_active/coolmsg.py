from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
from sms_module.util import get_secret

# set api key, api secret
api_key = get_secret("api_key")
api_secret = get_secret("api_secret")


def sms_send(to_num, r_num):
    params = dict()
    params['type'] = 'sms'
    params['to'] = to_num
    params['from'] = get_secret("from_num")
    params['text'] = str(r_num)

    cool = Message(api_key, api_secret)
    try:
        res = cool.send(params)
        res['r_num'] = r_num
        return res

    except CoolsmsException as e:
        print("Error Code : %s" % e.code)
        print("Error Message : %s" % e.msg)
        raise e


def send(phone, r_num):
    try:
        res = sms_send(phone, r_num)
    except CoolsmsException:
        return {'res': False}

    res['res'] = True
    return res
