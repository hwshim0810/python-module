# Import django module
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
# Import private module
from tel_active.coolmsg import sms_send
from tel_active.models import AuthInfo
from sdk.exceptions import CoolsmsException
from sms_module.util import gen_num
# Import regex module
import re


def index(request):
    if request.method == "POST":
        to_num = request.POST['phone']
        r_num = gen_num(6)

        if not bool(re.search(r"^[0-9]*$", to_num)):
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
            AuthInfo(phone=to_num, msg=r_num).save()
            return render(request, 'auth/certify.html')
        else:
            return render(request, 'error/send_err.html')

    else:
        return render(request, 'auth/index.html')
