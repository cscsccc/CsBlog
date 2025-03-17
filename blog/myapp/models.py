from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
import markdown
import re
from django.utils import timezone

# Create your models here.
class BlogInformation(models.Model):
    category = models.CharField(max_length=10)
    author = models.CharField(max_length=100, default='Cs')
    title = models.CharField(max_length=20)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.title
    
    @classmethod
    def get_latest(cls):
        records = cls.objects.all().order_by('-time')
        formatted_records = [
            {
                'id': record.id,
                'category': record.category,
                'title': record.title,
                'content': re.sub('<[^<]+?>', '', markdown.markdown(record.content)),
                'time': record.time.strftime('%Y年%m月%d日 %H:%M'),
                'views': record.views,
                'author': record.author if record.author else 'CS'
            }
            for record in records
        ]
        return formatted_records

class Comment(models.Model):
    blog = models.ForeignKey(BlogInformation, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.blog}'

class EmailVerificationCode(models.Model):
    email = models.EmailField()
    code_register = models.CharField(max_length=6, blank=True, null=True)
    code_reset = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at_register = models.DateTimeField(blank=True, null=True)
    updated_at_reset = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.email
class ViewRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(BlogInformation, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')