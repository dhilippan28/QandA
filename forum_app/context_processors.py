from .models import Notification

def user_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {
            'unread_notification_count': unread_count
        }
    return {}
