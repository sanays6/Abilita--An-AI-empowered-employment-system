from django.db import models

class DomainExpert(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    domain = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class InterviewQuestion(models.Model):
    domain = models.CharField(max_length=100)
    question_text = models.TextField()

    def __str__(self):
        return f"{self.domain} - {self.question_text[:50]}"
