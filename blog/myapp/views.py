from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import get_token
import json
import markdown
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import random
import string
from django.core.mail import send_mail
from django.utils import timezone
from .models import *
from datetime import timedelta
from django.core.files.storage import default_storage
from rest_framework_simplejwt.tokens import RefreshToken
from functools import wraps
from rest_framework.exceptions import AuthenticationFailed

# Create your views here.

view_blog = {}

# 获取所有博客
def get_data(request):
    data = BlogInformation.get_latest()
    return JsonResponse(data, safe=False)

def getBlogDetail(request, id):
    try:
            # print(id)
            blog = get_object_or_404(BlogInformation, id=id)
            username_now = request.GET.get('username')
            if username_now:
                user = get_object_or_404(User, username=username_now)
                if not ViewRecord.objects.filter(user=user, blog=blog).exists():
                # 如果没有访问记录，则创建一条新记录
                    ViewRecord.objects.create(user=user, blog=blog)

                    # 在此处你可以增加博客的访客数量
                    blog.views += 1
                    blog.save()
            # print(blog)
            comments = blog.comments.all()
        
            # 将评论数据序列化为字典列表
            comments_data = [
                {
                    'author': comment.author,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y年%m月%d日 %H:%M')
                }
                for comment in comments
            ]
            response = {
                'id': blog.id,
                'category': blog.category,
                'title': blog.title,
                # 'content': markdown.markdown(blog.content, extensions=extensions),
                'content': blog.content,
                'time': blog.time.strftime('%Y年%m月%d日 %H:%M'),
                'views': blog.views,
                'comments': comments_data,
                'author': blog.author if blog.author else 'CS'
            }
            return JsonResponse(response, safe=False)
    except BlogInformation.DoesNotExist:
        return JsonResponse({'error': 'Blog not found'}, status=404)

@csrf_exempt
def loginAuth(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # 验证用户
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({'success':False, 'message':'找不到此用户！'})
        else:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return JsonResponse({'success':True, 'message':'登陆成功', 'data': {'jwtToken': str(refresh.access_token)}})
    
    return JsonResponse({'success': False, 'message': 'Method Not Allowed'}, status=405)

@csrf_exempt
def userLogout(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logout successful'})


@csrf_exempt
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        verification_code = request.POST.get('vercode')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not all([email, verification_code, username, password]):
            return JsonResponse({'success': False, 'message': 'All fields are required.'})

        # 查找与给定email和验证码匹配的记录
        try:
            verification_record = EmailVerificationCode.objects.filter(email=email, code_register=verification_code).latest('created_at')
        except EmailVerificationCode.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid verification code or email.'})
        except EmailVerificationCode.MultipleObjectsReturned:
            return JsonResponse({'success': False, 'message': 'Multiple verification records found. Please contact support.'})

        # 检查验证码是否在有效期内
        if timezone.now() - verification_record.updated_at_register < timedelta(minutes=6):
            # 确保用户名唯一
            if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                # 创建用户
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                return JsonResponse({'success': True, 'message': 'User created successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Username already exists.'})
        else:
            return JsonResponse({'success': False, 'message': 'Verification code has timeout.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@csrf_exempt
def submitBlog(request):
    try:
        data = json.loads(request.body)
        category = data.get("category")
        content = data.get("content")
        title = data.get('title')
        username = data.get('username')

        # 创建博客信息
        BlogInformation.objects.create(
            title=title,
            author = username,
            content=content,
            category=category
        )

        # 成功返回响应
        return JsonResponse({'success': True, 'message': 'Blog submitted successfully', 'data': data})

    except Exception as e:
        # 捕获异常并返回错误响应
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@csrf_exempt
def send_verification_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        if email:
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'User already exists..'})

            code = generate_verification_code()
            subject = 'CsBlog verification code'
            message = f'Hello!Your verification code is {code}'
            from_email = 'cscs53546@gmail.com'
            recipient_list = [email]
            
            # Send email
            send_mail(subject, message, from_email, recipient_list)
            
            # Save the verification code and email to the database
            EmailVerificationCode.objects.update_or_create(email=email, defaults={'code_register': code,'updated_at_reset': timezone.now()})
            
            return JsonResponse({'success': True, 'message': 'send successfully! '})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@csrf_exempt
def submitComment(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        blogId = request.POST.get('blogId')
        comment = request.POST.get('comment')
        blog = BlogInformation.objects.get(id=blogId)
        Comment.objects.create(blog=blog, content=comment, author=username)

        return JsonResponse({'success': True, 'message':'评论成功！'})
    return JsonResponse({'success': False, 'message':'请求方式出错！'})



@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.url(file_name)
        print(file_url)
        return JsonResponse({'success': True, 'url': file_url, 'title': file_name})
    return JsonResponse({'success': False, 'message': '上传失败，应为POST请求。'}, status=400)

@csrf_exempt
def send_reset_vercode(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        
        if email:
            if not User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': '数据库无此邮箱.'})
            code = generate_verification_code()
            subject = 'CsBlog verification code'
            message = f'Hello!Your reset verification code is {code}'
            from_email = 'cscs53546@gmail.com'
            recipient_list = [email]
            
            try:
                # Send email
                send_mail(subject, message, from_email, recipient_list)

                # Save the verification code and email to the database
                EmailVerificationCode.objects.update_or_create(email=email, defaults={'code_reset': code,'updated_at_register': timezone.now()})

                return JsonResponse({'success': True, 'message': 'send successfully! '})
            except Exception as e:
                print(f"Error sending email: {e}")
                return JsonResponse({'success': False, 'message': 'Failed to send verification code.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@csrf_exempt
def find_pwd(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        verification_code = request.POST.get('vercode')
        reset_password = request.POST.get('reset_password')

        if not all([email, verification_code, reset_password]):
            return JsonResponse({'success': False, 'message': 'All fields are required.'})
        
        try:
            verification_record = EmailVerificationCode.objects.filter(email=email, code_reset=verification_code).latest('created_at')
        except EmailVerificationCode.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid verification code or email.'})
        except EmailVerificationCode.MultipleObjectsReturned:
            return JsonResponse({'success': False, 'message': 'Multiple verification records found. Please contact support.'})

        if timezone.now() - verification_record.updated_at_register < timedelta(minutes=6):
            user = get_object_or_404(User, email=email)
            user.set_password(reset_password)
            user.save()
            return JsonResponse({'success':True,'message':'修改密码成功'})
        else:
            return JsonResponse({'success':False,'message':'验证码已超时'})
    return JsonResponse({'success':False, 'message':'Request Error'})



# @ensure_csrf_cookie
# def get_csrf_cookie(request):
#     token = get_token(request)
#     print(token)
#     return JsonResponse({'csrfToken': token})
def get_csrf_token(request):
    csrf_token = get_token(request)  # 获取csrf_token的值
    print(csrf_token)
    return JsonResponse({'token': csrf_token})

# class login():
#     def get():



