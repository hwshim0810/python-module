# Import django module
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
# Import private module
from tel_active.coolmsg import sms_send
from tel_active.models import AuthInfo
from sdk.exceptions import CoolsmsException
# Import regex module
import re
# Import Util module
from operator import eq
from sms_module.util import gen_num, get_secret
from sms_module.crypto import AESCipher


key = get_secret("crypto_key")


def index(request):
    if request.method == "POST":
        to_num = request.POST['phone']
        r_num = gen_num(6)

        if not bool(re.search(r"^[0-9]*$", to_num)) or len(to_num) <= 10:
            return render(request, 'error/send_err.html')

        # Delete old auth_info
        try:
            AuthInfo.objects.get(phone=to_num).delete()
        except ObjectDoesNotExist:
            pass

        # Send Message & Insert auth_num
        try:
            res = sms_send(to_num, r_num)
        except CoolsmsException:
            return render(request, 'error/send_err.html')

        if int(res["success_count"]) > 0:
            # 인증번호 암호화 후 DB저장
            r_num = AESCipher(key).encrypt(r_num)
            AuthInfo(phone=to_num, msg=r_num).save()
            return render(request, 'auth/certify.html', {'to_num': to_num})
        else:
            return render(request, 'error/send_err.html')

    # Not form
    else:
        return render(request, 'auth/index.html')


def certify(request):
    msg = request.POST['msg']
    db_msg = AuthInfo.objects.get(phone=request.POST['to_num'])

    # 인증은 3회까지
    if db_msg.counter > 1:
        db_msg.delete()
        return render(request, 'error/count_err.html')
    # DB정보와 입력정보 대조하여 인증여부 결정
    if eq(msg, AESCipher(key).decrypt(str(db_msg.msg))):
        db_msg.delete()
        return HttpResponseRedirect('/welcome')
    # 틀렸을 경우 기회차감
    else:
        db_msg.counter = db_msg.counter + 1
        db_msg.save()
        return render(request, 'error/auth_err.html', {'id': db_msg.id})


# 인증번호 틀렸을 경우 재시도를 위한 Form
def cer_form(request, msg_id):
    db_msg = AuthInfo.objects.get(id=msg_id)
    return render(request, 'auth/certify.html', {'to_num': db_msg.phone})


def welcome(request):
    return render(request, 'auth/auth_complete.html')
