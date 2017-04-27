# Import django module
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
# Import private module
from tel_active.coolmsg import send
from tel_active.models import AuthInfo

# Import Util module
from sms_module.util import gen_num, get_secret


key = get_secret("crypto_key")


def index(request):
    if request.method == "POST":
        phone = request.POST['phone']
        r_num = gen_num(6)

        if AuthInfo.validate_phone(phone):
            return render(request, 'error/send_err.html')

        # Delete old auth_info
        try:
            AuthInfo.get_info_by_num(phone).delete()
        except ObjectDoesNotExist:
            pass

        # Send Message
        res = send(phone, r_num)
        if not res['res']:
            return render(request, 'error/send_err.html')

        # Insert auth_num
        if AuthInfo.insert_info(res, r_num, phone):
            return render(request, 'auth/certify.html', {'phone': phone})
        else:
            return render(request, 'error/send_err.html')

    # Not form
    else:
        return render(request, 'auth/index.html')


# 인증번호 확인
def certify(request):
    msg = request.POST['msg']
    info = AuthInfo.get_info_by_num(phone=request.POST['to_num'])

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
    return render(request, 'auth/certify.html', {'phone': AuthInfo.get_info_by_id(msg_id).phone})


# 성공화면
def welcome(request):
    return render(request, 'auth/auth_complete.html')
