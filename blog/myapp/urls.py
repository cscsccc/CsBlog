from django.urls import path
from .views import *
urlpatterns = [
    # path("", taskList.as_view(), name = 'tasklist'),
    # path("detail/<int:pk>/", taskDetail.as_view(),name='taskdetail'),
    # path("index/", index, name = 'index')
    # path("multiply_upload/", , name='multiply_upload')
    path("data/",get_data),
    # path("data/lastedItems", getLastedData),
    path("blog/<int:id>/", getBlogDetail),
    path("login/", loginAuth),
    path("submitblog/", submitBlog),
    path('get_csrf_token/', get_csrf_token,name='get_csrf_token'),
    path("register/", register),
    path('send_verification_code/', send_verification_code, name='send_verification_code'),
    path('send_reset_vercode/', send_reset_vercode, name='send_reset_vercode'),
    path('findpwd/', find_pwd, name='to_find_password'),

    path('submitComment/', submitComment, name='submit_comment'),
    path("logout/", userLogout),
    path('upload_image/', upload_image, name='upload_image'),
    # path("csrf_token/", get_csrf_cookie)
]