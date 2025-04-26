from base64 import b64encode
from accounts.models import Profile

def avatar_context(request):
    """
    Pass the avatar_base64 globally to all templates for authenticated users.
    """
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        avatar_base64 = None
        if profile and profile.avatar:
            avatar_base64 = b64encode(profile.avatar).decode('utf-8')
        return {'avatar_base64': avatar_base64}
    return {}