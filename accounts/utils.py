# accounts/utils.py

def get_user_school(request):
    if request.user.is_authenticated:
        return request.user.school
    return None