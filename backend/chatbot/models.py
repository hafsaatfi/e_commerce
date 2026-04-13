from django.db import models

# Create your models here.
from django.db import models
from users.models import Utilisateur

class Log_Chatbot(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    question = models.TextField()
    reponse = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)