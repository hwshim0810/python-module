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
    info = AuthInfo.get_info_by_num(request.POST['to_num'])

    # 유효인증횟수 검사
    if info.validate_count():
        return render(request, 'error/count_err.html')

    # 입력정보와 대조검사
    res = info.validate_info(msg)
    if res['res']:
        return HttpResponseRedirect('/welcome')
    else:
        return render(request, 'error/auth_err.html', {'id': res['id']})


# 인증번호 틀렸을 경우 재시도를 위한 Form
def cer_form(request, msg_id):
    return render(request, 'auth/certify.html', {'to_num': AuthInfo.get_info_by_id(msg_id).phone})

# 성공화면
def welcome(request):
    return render(request, 'auth/auth_complete.html')
