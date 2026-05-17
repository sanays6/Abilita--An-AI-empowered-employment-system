from django.db import models

class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email

class AptitudeQuestion(models.Model):
    domain = models.CharField(max_length=100)
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.domain} - {self.question[:50]}"

class AIConfiguration(models.Model):
    api_key = models.CharField(max_length=500, blank=True, null=True)
    model_name = models.CharField(max_length=100, default='llama-3.1-8b-instant')
    
    def __str__(self):
        return self.model_name
