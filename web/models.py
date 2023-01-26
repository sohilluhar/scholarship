from django.db import models
from django.core.exceptions import ValidationError


class User(models.Model):
    mail = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    adhar_no = models.CharField(max_length=16, unique=True)
    profilefill = models.CharField(max_length=3)

    def __str__(self):
        return self.name

    def clean(self):
        if User.objects.filter(adhar_no=self.adhar_no).exclude(pk=self.pk).exists():
            raise ValidationError("Adhar Number already exists.")
        if User.objects.filter(phone=self.phone).exclude(pk=self.pk).exists():
            raise ValidationError("Phone Number already exists.")
        if User.objects.filter(mail=self.mail).exclude(pk=self.pk).exists():
            raise ValidationError("Email already exists.")


class AppliedUserScheme(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_scheme = models.CharField(max_length=255)


class UserProfile(models.Model):
    phone_number = models.TextField(max_length=10)
    account_number = models.TextField(max_length=256, null=True, default=None)
    achievement = models.TextField(max_length=256, null=True, default=None)
    address = models.TextField(max_length=256, null=True, default=None)
    age = models.TextField(max_length=256, null=True, default=None)
    annual_income = models.TextField(max_length=256, null=True, default=None)
    bank_name = models.TextField(max_length=256, null=True, default=None)
    cast = models.TextField(max_length=256, null=True, default=None)
    collegeaddress = models.TextField(max_length=256, null=True, default=None)
    collegeheadname = models.TextField(max_length=256, null=True, default=None)
    collegename = models.TextField(max_length=256, null=True, default=None)
    course1board = models.TextField(max_length=256, null=True, default=None)
    course1marks = models.TextField(max_length=256, null=True, default=None)
    course1markstotal = models.TextField(max_length=256, null=True, default=None)
    course1medium = models.TextField(max_length=256, null=True, default=None)
    course1name = models.TextField(max_length=256, null=True, default=None)
    course1per = models.TextField(max_length=256, null=True, default=None)
    course1year = models.TextField(max_length=256, null=True, default=None)
    course2board = models.TextField(max_length=256, null=True, default=None)
    course2marks = models.TextField(max_length=256, null=True, default=None)
    course2markstotal = models.TextField(max_length=256, null=True, default=None)
    course2medium = models.TextField(max_length=256, null=True, default=None)
    course2name = models.TextField(max_length=256, null=True, default=None)
    course2per = models.TextField(max_length=256, null=True, default=None)
    course2year = models.TextField(max_length=256, null=True, default=None)
    course3board = models.TextField(max_length=256, null=True, default=None)
    course3name = models.TextField(max_length=256, null=True, default=None)
    course3per = models.TextField(max_length=256, null=True, default=None)
    course3year = models.TextField(max_length=256, null=True, default=None)
    courseacademicyear = models.TextField(max_length=256, null=True, default=None)
    courseduration = models.TextField(max_length=256, null=True, default=None)
    coursefees = models.TextField(max_length=256, null=True, default=None)
    coursefeespaid = models.TextField(max_length=256, null=True, default=None)
    coursefeesrequired = models.TextField(max_length=256, null=True, default=None)
    coursename = models.TextField(max_length=256, null=True, default=None)
    docaddressname = models.TextField(max_length=256, null=True, default=None)
    docaddressurl = models.TextField(max_length=256, null=True, default=None)
    docadmissionname = models.TextField(max_length=256, null=True, default=None)
    docadmissionurl = models.TextField(max_length=256, null=True, default=None)
    docageproofname = models.TextField(max_length=256, null=True, default=None)
    docageproofurl = models.TextField(max_length=256, null=True, default=None)
    doccourse1url = models.TextField(max_length=256, null=True, default=None)
    doccourse2url = models.TextField(max_length=256, null=True, default=None)
    doccourse3url = models.TextField(max_length=256, null=True, default=None)
    doccurrentfeename = models.TextField(max_length=256, null=True, default=None)
    doccurrentfeeurl = models.TextField(max_length=256, null=True, default=None)
    docincomename = models.TextField(max_length=256, null=True, default=None)
    docincomeurl = models.TextField(max_length=256, null=True, default=None)
    docpassbookurl = models.TextField(max_length=256, null=True, default=None)
    fname = models.TextField(max_length=255, null=True, default=None)
    sname = models.TextField(max_length=255, null=True, default=None)
    lname = models.TextField(max_length=255, null=True, default=None)
    email = models.TextField(max_length=256, null=True, default=None)
    phone = models.TextField(max_length=10, null=True, default=None)
    gender = models.TextField(max_length=10, null=True, default=None)
    dob = models.TextField(max_length=256, null=True, default=None)
    religious = models.TextField(max_length=255, null=True, default=None)
    parent_status = models.TextField(max_length=255, null=True, default=None)
    parent_phone = models.TextField(max_length=10, null=True, default=None)
    fathername = models.TextField(max_length=255, null=True, default=None)
    fatheroccupation = models.TextField(max_length=255, null=True, default=None)
    fatherincome = models.TextField(max_length=256, null=True, default=None)
    fatheralive = models.TextField(max_length=256, null=True, default=None)
    mothername = models.TextField(max_length=255, null=True, default=None)
    motheroccupation = models.TextField(max_length=255, null=True, default=None)
    motherincome = models.TextField(max_length=256, null=True, default=None)
    motheralive = models.TextField(max_length=256, null=True, default=None)
    totalearningmember = models.TextField(max_length=256, null=True, default=None)
    totalfamilymember = models.TextField(max_length=256, null=True, default=None)
    family_income = models.TextField(max_length=256, null=True, default=None)
    lastcoursename = models.TextField(max_length=255, null=True, default=None)
    lastcourseacademicyear = models.TextField(max_length=255, null=True, default=None)
    nameinpassbook = models.TextField(max_length=255, null=True, default=None)
    ifsc_code = models.TextField(max_length=255, null=True, default=None)
    pincode = models.TextField(max_length=6, null=True, default=None)
    docphotoidname = models.TextField(max_length=255, null=True, default=None)
    docphotoidurl = models.TextField(max_length=255, null=True, default=None)

    def __str__(self):
        return self.phone_number


class Trust(models.Model):
    trust_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=True)
    about = models.CharField(max_length=255,null=True)
    address = models.CharField(max_length=255,null=True)
    contact = models.CharField(max_length=255, null=True)
    logo = models.CharField(max_length=255,null=True)
    mailid = models.EmailField(null=True)
    password = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, null=True)
    vision = models.CharField(max_length=255,null=True)

    def __str__(self):
        return self.name


class Scheme(models.Model):
    name = models.CharField(max_length=255, null=True)
    trust_id = models.CharField(max_length=255, null=True)
    level = models.CharField(max_length=255, null=True)
    course = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    eligibility = models.CharField(max_length=255,null=True)
    lastdate = models.CharField(max_length=255, null=True)
    logo = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class AppliedScheme(models.Model):
    scheme_id = models.CharField(max_length=255, null=True)
    scheme_name = models.CharField(max_length=255, null=True)
    tname = models.CharField(max_length=255, null=True)
    trust_id = models.CharField(max_length=255, null=True)
    userid = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)
    schemeamount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    sanctionedamount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    interviewdate = models.CharField(max_length=255, blank=True, null=True)
    remark = models.CharField(max_length=255,null=True)
    applicationid = models.CharField(max_length=255, null=True)

