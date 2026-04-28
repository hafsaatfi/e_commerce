from django.http import HttpResponse

from users.permissions import admin_required

@admin_required
def home(request):
    return HttpResponse("Chatbot OK ✔")