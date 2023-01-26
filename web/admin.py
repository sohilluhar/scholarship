from django.contrib import admin
from .models import AppliedUserScheme,User,UserProfile,Trust
# Register your models here.
admin.site.register(User)
admin.site.register(AppliedUserScheme)
admin.site.register(UserProfile)
admin.site.register(Trust)
