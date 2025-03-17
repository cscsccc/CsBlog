from django.contrib import admin
from .models import BlogInformation, EmailVerificationCode, Comment
# Register your models here.
admin.site.register(BlogInformation)
admin.site.register(EmailVerificationCode)
admin.site.register(Comment)