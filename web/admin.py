from django.contrib import admin
from .models import AppliedUserScheme, User, UserProfile, Trust, Scheme,AppliedScheme

# Register your models here.
admin.site.register(User)
admin.site.register(AppliedUserScheme)
admin.site.register(UserProfile)
admin.site.register(Trust)
admin.site.register(Scheme)
admin.site.register(AppliedScheme)

"""
Scheme.objects.create(**data)

schemes = Scheme.objects.filter(trust_id=request.session['trustkey'])

Trust.objects.update_or_create(
            trust_id=tkey,
            defaults=data
        )

user = User.objects.get(phone=mail)
 Trust.objects.all().values()

"""