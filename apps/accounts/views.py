from django.shortcuts import render


def staff_login_view(request):
    return render(request, 'staff_login.html')

def admin_login_view(request):
    return render(request, 'admin_login.html')
