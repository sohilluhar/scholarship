import collections
from collections import OrderedDict
from datetime import datetime
from random import randint

import pyrebase
from cryptography.fernet import Fernet
from django.core import serializers
import json
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render

from web.form import UserForm
from web.models import User, UserProfile, Trust, Scheme, AppliedScheme
from . import Common
from . import PyConfig
from .SendMail import sendmail


def connect_firebase():
    firebase = pyrebase.initialize_app(PyConfig.config1)
    auth = firebase.auth()
    db = firebase.database()
    return db


def category(request, key):

    schemes = Scheme.objects.filter(level=request.GET['category'])

    return render(request, 'category.html',
                  {"scheme": schemes, "islog": True if 'isLogin' in request.session else False})


def home(request):
    db = connect_firebase()
    trusts =  Trust.objects.all()
    schemes = Scheme.objects.all().order_by('-id')[:9]
    print(schemes)
    isLogin = False
    if 'isLogin' in request.session:
        isLogin = True
    return render(request, 'home.html', {"scheme": schemes, "all_trusts": trusts, "islog": isLogin})


def login(request):
    return render(request, 'login.html', {})


def adminlogin(request):
    return render(request, 'adminlogin.html', {})


def adminverify(request):
    adminname = request.POST.get('trust_username')
    password = request.POST.get('password')

    # db = connect_firebase()
    # username = db.child("Admin").child("username").get().val()
    # passworddb = db.child("Admin").child("password").get().val()
    from django.contrib.auth import authenticate
    user = authenticate(username=adminname, password=password)
    if user is not None:

        #
        # Common.isAdminLogin = True
        # request.session['admin'] = db.child("Admin").get().val()

        request.session['isAdminLogin'] = True
        #request.session['admin'] = db.child("Admin").get().val()

        return HttpResponseRedirect('/adminhome')
    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Invalid Password or username",
                       "path": "admin-login"})


def adminhome(req):
    # if 'cart' not in request.session:
    if ('isAdminLogin' in req.session):
        data = Trust.objects.all().values()

        # db = connect_firebase()
        # try:
        #     data = db.child("Trust").get().val()
        # except:
        #     pass

        print(data)
        return render(req, 'admin_home.html',
                      { "trusts": data})
    else:
        return render(req, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def addtrust(req):
    if ('isAdminLogin' in req.session):

        timestamp = datetime.timestamp(datetime.now())
        trustkey = str(timestamp).replace('.', '')
        return render(req, 'addtrust.html',
                      {"trustkey": trustkey})
    else:
        return render(req, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def addtrustdb(request):
    if ('isAdminLogin' in request.session):
        tname = request.POST['tname']
        tcontact = request.POST['tcontact']
        temailid = request.POST['temailid']
        tabout = request.POST['tabout']
        taddress = request.POST['taddress']
        tvision = request.POST['tvision']
        tpass = request.POST['tpass']
        tkey = request.POST['trustkey']
        logo = request.POST['trustlogourl']
        print(logo)
        tlogo = "https://firebasestorage.googleapis.com/v0/b/scholar-help-966a2.appspot.com/o/trust_logo%2F" + tkey + ".png?alt=media"

        db = connect_firebase()

        if Trust.objects.filter(mailid=temailid).exists():
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "Trust Email Exists", "path": "addtrust"})
        elif Trust.objects.filter(contact=tcontact).exists():
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "Trust Phone Exists", "path": "addtrust"})
        else:

            data = {
                "name": tname, "contact": tcontact, "mailid": temailid,
                "about": tabout, "address": taddress, "vision": tvision, "password": tpass
                , "logo": tlogo, "username": tname,"trust_id":tkey

            }
            msgsend = "" \
                      "You have been register on scholarhelp. " \
                      "Your password is " \
                      "" + tpass + " ."
            print(data)


            #db.child("Trust").child(str(tkey)).update(data)
            Trust.objects.update_or_create(
                trust_id=tkey,
                defaults=data
            )
            sendmail(temailid, "Successfully Registered on Scholar Help -" + tkey
                     , msgsend
                     )

            return render(request, 'redirecthome.html',
                          {"swicon": "success", "swtitle": "Done", "swmsg": "Trust Added Successfully",
                           "path": "adminhome"})

    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def adminedittrustview(req):
    if ('isAdminLogin' in req.session):
        tkey = req.POST['tkey']
        db = connect_firebase()
        # tru = db.child("Trust").child(str(tkey)).get().val()
        tru = Trust.objects.get(trust_id=str(tkey))

        return render(req, 'admin_edit_trust.html',
                      {"trustkey": str(tkey), "trust_val": tru})
    else:
        return render(req, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def adminstudentview(req):
    if ('isAdminLogin' in req.session):
        db = connect_firebase()
        try:
            data = User.objects.all()
        except:
            pass

        return render(req, 'view_all_student.html',
                      {"admin": req.session['admin'], "Users": data})

    else:
        return render(req, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def studentprofile(req):
    if ('isAdminLogin' in req.session):
        tkey = req.POST['tkey']
        db = connect_firebase()
        userprofile = None
        accno = None
        try:
            userprofile = db.child("UserProfile").child(str(tkey)).get().val()
            userprofile =UserProfile.objects.get(phone_number=str(tkey))

        except:
            pass
        return render(req, 'student_comp_profile.html',
                      {

                          "userprofile": userprofile,

                      })


    else:
        return render(req, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def removestudent(req):
    return render(req, 'redirecthome.html',
                  {"swicon": "success", "swtitle": "Done", "swmsg": "Can't Remove ",
                   "path": "adminhome"})
    # if ('isAdminLogin' in req.session):
    #     tkey = req.POST['tkey']
    #     db = connect_firebase()
    #     userprofile = None
    #     accno = None
    #     try:
    #         db.child("UserProfile").child(str(tkey)).remove()
    #
    #     except:
    #         pass
    #     try:
    #         db.child("users").child(str(tkey)).remove()
    #
    #     except:
    #         pass
    #     try:
    #         print(tkey + "user id")
    #         userapp = db.child("AppliedScheme").order_by_child("userid").equal_to(str(tkey)).get().val()
    #         all11 = db.child("AppliedScheme").get().val()
    #         all(map(all11.pop, userapp))
    #         db.child("AppliedScheme").set(all11)
    #     except:
    #         pass
    #     return render(req, 'redirecthome.html',
    #                   {"swicon": "success", "swtitle": "Done", "swmsg": "Student Remove Successfully",
    #                    "path": "adminhome"})
    #
    #
    # else:
    #     return render(req, 'redirecthome.html',
    #                   {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def removetrust(req):
    return render(req, 'redirecthome.html',
                  {"swicon": "success", "swtitle": "Done", "swmsg": "Can't Remove ",
                   "path": "adminhome"})
    # if ('isAdminLogin' in req.session):
    #     tkey = req.POST['tkey']
    #     db = connect_firebase()
    #     userprofile = None
    #     print(tkey + " tt")
    #     accno = None
    #     try:
    #         tt = db.child("Trust").child(str(tkey)).remove()
    #         print(tt + " tt")
    #
    #     except:
    #         pass
    #
    #     try:
    #
    #         tscheme = db.child("Scheme").order_by_child("trust_id").equal_to(str(tkey)).get().val()
    #         alls = db.child("Scheme").get().val()
    #         all(map(alls.pop, tscheme))
    #         db.child("Scheme").set(alls)
    #     except:
    #         pass
    #     try:
    #
    #         ascheme = db.child("AppliedScheme").order_by_child("trust_id").equal_to(str(tkey)).get().val()
    #         allaps = db.child("AppliedScheme").get().val()
    #         all(map(allaps.pop, ascheme))
    #         db.child("AppliedScheme").set(allaps)
    #     except:
    #         pass
    #     return render(req, 'redirecthome.html',
    #                   {"swicon": "success", "swtitle": "Done", "swmsg": "Trust Remove Successfully",
    #                    "path": "adminhome"})
    #
    #
    # else:
    #     return render(req, 'redirecthome.html',
    #                   {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def adminupdattrust(request):
    if ('isAdminLogin' in request.session):
        tname = request.POST['tname']
        tcontact = request.POST['tcontact']
        temailid = request.POST['temailid']
        tabout = request.POST['tabout']
        taddress = request.POST['taddress']
        tvision = request.POST['tvision']
        tpass = request.POST['tpass']
        tkey = request.POST['tkey']

        data = {
            "name": tname, "contact": tcontact, "mailid": temailid,
            "about": tabout, "address": taddress, "vision": tvision, "password": tpass
        }
        # db.child("Trust").child(tkey).update(data)
        Trust.objects.update_or_create(
            trust_id=tkey,
            defaults=data
        )

        return render(request, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Trust Updated Successfully",
                       "path": "adminhome"})

    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def trust_login(request):
    if 'isTrustLogin' not in request.session:
     return render(request, 'trust_login.html', {})
    else:

        return HttpResponseRedirect('/trusthome')


def forgotpass(request):
    return render(request, 'forgotpass.html', {})


def sendotp(request):
    db = connect_firebase()
    user = OrderedDict()
    getmail = request.POST['mail']
    try:
        user = db.child("users").order_by_child("mail").equal_to(getmail).get().val()
    except:
        print("Error")

    if not user:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Mail Id is not registered",
                       "path": "forgotpassword"})

    otp = str(randint(1000, 9999))
    # Common.forgotpassotp = otp
    request.session['forgotpassotp'] = otp
    request.session['forgotpassotptime'] = datetime.now()
    # Common.forgotpassotptime = datetime.now()
    title = "Reset Your Password"
    msg = "Enter following OTP within 15 minutes to change your password.\nOTP is " + otp
    for key, value in user.items():
        request.session['userphone'] = key
        # Common.userphone = key

    sendmail(getmail, title, msg)
    return HttpResponseRedirect('/verifyotp')


def verifyotp(request):
    return render(request, 'verifyotp.html', {})


def checkotp(request):
    getOTP = request.POST['otp']
    diff = datetime.now() - request.session['forgotpassotptime']
    otptime = diff.total_seconds()
    if getOTP != request.session['forgotpassotp']:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Wrong OTP Entered", "path": "verifyotp"})
    elif otptime > 15 * 60:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "OTP Expired", "path": "login"})
    else:
        return HttpResponseRedirect('/changepassword')


def changepassword(request):
    return render(request, 'changepassword.html', {})


def updatepassword(request):
    new_password = request.POST['pass']

    User.objects.filter(phone=request.session['currentUser']).update(password=new_password)

    return render(request, 'redirecthome.html',
                  {"swicon": "success", "swtitle": "Done", "swmsg": "Password Changed Successfully.",
                   "path": "login"})


def verify(request):
    if 'isLogin' not in request.session:
        mail = request.POST.get('mail')
        password = request.POST.get('password')

        # db = connect_firebase()
        # user = db.child("users").child(mail).get()

        if not User.objects.filter(phone=mail).exists():
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "User does not exists", "path": "login"})
        else:
            user = User.objects.get(phone=mail)
            if password == user.password:

                request.session['currentUser'] = user.phone
                request.session['isLogin'] = True

                return HttpResponseRedirect('/')
            else:
                return render(request, 'redirecthome.html',
                              {"swicon": "error", "swtitle": "Error", "swmsg": "Invalid Password",
                               "path": "login"})
    else:
        # c = {'user': req.session['currentUser'].val()}
        return HttpResponseRedirect('/')


def trust_verify(request):
    if 'isTrustLogin' not in request.session:
        trustusername = request.POST.get('trust_username')
        password = request.POST.get('password')

        # print(password)
        # db = connect_firebase()
        # trust = None
        # try:
        #     user = db.child("Trust").order_by_child("mailid").equal_to(trustusername).get().val()
        #
        #     for key, value in user.items():
        #         trustkey = key
        #         trust = value
        # except:
        #     pass

        if not Trust.objects.filter(mailid=trustusername).exists():
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "Incorrect UserID or Password", "path": "trustlogin"})
        else:
            user = Trust.objects.get(mailid=trustusername)
            if password == user.password:
                # Common.trustkey = trustkey
                # Common.trustVal = trust
                # Common.isTrustLogin = True

                request.session['trustkey'] = user.trust_id
                # request.session['trustVal'] = trust
                request.session['isTrustLogin'] = True

                return HttpResponseRedirect('/trusthome')
            else:
                return render(request, 'redirecthome.html',
                              {"swicon": "error", "swtitle": "Error", "swmsg": "Incorrect UserID or Password",
                               "path": "trustlogin"})
    else:

        return HttpResponseRedirect('/trusthome')


def trust_home(req):
    if ('isTrustLogin' in req.session):
        data = AppliedScheme.objects.filter(trust_id=req.session['trustkey'])

        # db = connect_firebase()
        # try:
        #     data = db.child("AppliedScheme").order_by_child("trust_id").equal_to(req.session['trustkey']).get().val()
        #     data = collections.OrderedDict(reversed(list(data.items())))
        # except:
        #     pass
        #
        # print(data)
        return render(req, 'trust_home.html',
                      {"trustkey": req.session['trustkey'],
                       "applied_schemes": data})
    else:
        return render(req, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def viewtakeaction(request):
    userphone = request.POST['userphone']
    applicationid = request.POST['applicationid']

    if ('isTrustLogin' in request.session):

        db = connect_firebase()
        applied = OrderedDict()
        amount_received = 0
        # application = db.child("AppliedScheme").child(applicationid).get().val()
        application = AppliedScheme.objects.get(applicationid=applicationid)
        # userprofile = db.child("UserProfile").child(userphone).get().val()
        userprofile = UserProfile.objects.get(phone_number=userphone)

        pendingamt = int(userprofile.coursefees)
        # schemeeligibility = db.child("Scheme").child(application.get("scheme_id")).child("eligibility").get().val()
        schemeeligibility = Scheme.objects.get(id=application.scheme_id).eligibility

        # userappliedscholarship = db.child("AppliedScheme").order_by_child("userid").equal_to(userphone).get().val()
        userappliedscholarship = AppliedScheme.objects.filter(userid=userphone).exclude(applicationid=applicationid)
        # del userappliedscholarship[applicationid]
        print(userappliedscholarship)

        for value in userappliedscholarship:
            print(value.applicationid, "is ", value.status)
            if value.status == "Approve":
                print(value, "is approve")
                amount_received += int(value.sanctionedamount)
                tmp = {value.applicationid: value}
                applied.update(tmp)
                print(applied)
        pendingamt = pendingamt - amount_received
        return render(request, 'trust_takeaction.html',
                      {"trustkey": request.session['trustkey'],
                       "application": application, "applicationid": applicationid,
                       "userprofile": userprofile, "appliedscholarship": applied,
                       "amtrec": str(amount_received), "amtpen": str(pendingamt), "schemeeligibility": schemeeligibility

                       })
    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def updateapplicationstatus(request):
    if ('isTrustLogin' in request.session):
        applicationid = request.POST['applicationid']
        status = request.POST['status']
        interviewdate = request.POST['interviewdate']
        sancamt = request.POST['sancamt']
        remark = request.POST['remark']
        mail = request.POST['mail']
        schemename = request.POST['schemename']
        if sancamt=='':
            sancamt=0
        data = {
            "interviewdate": interviewdate, "status": status, "sanctionedamount": sancamt,
            "remark": remark
        }
        # db = connect_firebase()
        # db.child("AppliedScheme").child(applicationid).update(data)
        AppliedScheme.objects.update_or_create(
            applicationid=applicationid,
            defaults=data
        )

        title = "ScholarHelp - Status updated fo applicatiod id " + applicationid
        msg = "Your application status for " + schemename + " has been updated to " + status + ".Please login to " \
                                                                                               "ScholarHelp to view " \
                                                                                               "more details. "
        print(msg)
        sendmail(mail, title, msg)
        return render(request, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Application Status Updated Successfully",
                       "path": "trusthome"})

    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def viewtrustprofile(request):
    # db = connect_firebase()
    # request.session['trustVal'] = db.child("Trust").child(request.session['trustkey']).get().val()
    trust_val=Trust.objects.get(trust_id=request.session['trustkey'])
    return render(request, 'trust_profile.html',
                  {"trustkey": request.session['trustkey'], "trust_val": trust_val})


def updatetrustprofile(request):
    if ('isTrustLogin' in request.session):
        tname = request.POST['tname']
        tcontact = request.POST['tcontact']
        temailid = request.POST['temailid']
        tabout = request.POST['tabout']
        taddress = request.POST['taddress']
        tvision = request.POST['tvision']
        tpass = request.POST['tpass']

        data = {
            "name": tname, "contact": tcontact, "mailid": temailid,
            "about": tabout, "address": taddress, "vision": tvision, "password": tpass
        }
        # db = connect_firebase()
        # db.child("Trust").child(request.session['trustkey']).update(data)
        Trust.objects.update_or_create(
            trust_id=request.session['trustkey'],
            defaults=data
        )

        return render(request, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Profile Updated Successfully",
                       "path": "trusthome"})

    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def addscholarhip(req):
    if ('isTrustLogin' in req.session):
        return render(req, 'add_scholarship.html',
                      {"trustkey": req.session['trustkey']})
    else:
        return render(req, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": ""})


def viewallscholarships(request):
    # schemes = OrderedDict()
    schemes = Scheme.objects.filter(trust_id=request.session['trustkey'])
    # db = connect_firebase()
    # try:
    #     schemes = db.child("Scheme").order_by_child("trust_id").equal_to(request.session['trustkey']).get().val()
    # except:
    #     print("Error")
    return render(request, 'trust_allscheme.html',
                  {"trustkey": request.session['trustkey'],
                   "scholarships": schemes
                   })


def register(request):
    form = UserForm()
    return render(request, 'register.html',{'form': form})


def trust_logout(request):
    del request.session['trustkey']
    #del request.session['trustVal']
    del request.session['isTrustLogin']
    # 'isTrustLogin' in req.session = False
    # req.session['isLogin'] = False

    return render(request, 'redirecthome.html',
                  {"swicon": "success", "swtitle": "Done", "swmsg": "Logout Successfully", "path": ""})


def adminlogout(request):
    del request.session['isAdminLogin']
    return render(request, 'redirecthome.html',
                  {"swicon": "success", "swtitle": "Done", "swmsg": "Logout Successfully", "path": ""})


def logout(request):
    del request.session['isLogin']
    del request.session['currentUser']
    return render(request, 'redirecthome.html',
                  {"swicon": "success", "swtitle": "Done", "swmsg": "Logout Successfully", "path": ""})


def adduser(req):
    name = req.POST['name']
    email = req.POST['mail']
    phone = req.POST['phone']
    passwrd = req.POST['pass']
    adhar_no = req.POST['adhar_no']
    useremail = None
    db = connect_firebase()
    user = db.child("users").child(phone).get()
    userdict={'mail':email,'name':name,'password':passwrd,'phone':phone,'adhar_no':adhar_no,'profilefill':0}
    # if req.method == 'POST':
    #     form = UserForm(req.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('user_list')
    # else:
    #     form = UserForm()
    # return render(request, 'web/user_form.html', {'form': form})
    # useremail = db.child("users").order_by_child("mail").equal_to(email).get().val()
    user = User(
mail        = email ,
name        =    name   ,
password    =passwrd       ,
phone       =    phone   ,
adhar_no    =   adhar_no    ,
profilefill =0
    )
    # user = User.objects.create(**userdict)
    try:
            user.full_clean()
            user.save()
            return render(req, 'redirecthome.html',
                          {"swicon": "success", "swtitle": "Done", "swmsg": "Registration Done Successfully.",
                           "path": "login"})

    except ValidationError as e:
        errVal=e.messages
        err=""
        error_list = e.error_dict.get('__all__')
        for errmsg in error_list:
            err+=errmsg.message

        return render(req, 'redirecthome.html',
                              {"swicon": "error", "swtitle": "Error", "swmsg":err, "path": "register"})


        # else:
        #     print("Invalid ")
        #     return render(req, 'redirecthome.html',
        #                       {"swicon": "error", "swtitle": "Error", "swmsg": "User Already Exists", "path": "register"})
    # print(useremail)
    # if user.val():
    #     return render(req, 'redirecthome.html',
    #                   {"swicon": "error", "swtitle": "Error", "swmsg": "User Already Exists", "path": "register"})
    # elif useremail:
    #     return render(req, 'redirecthome.html',
    #                   {"swicon": "error", "swtitle": "Error", "swmsg": "User Mail Exists", "path": "register"})
    # else:
    #     data = {
    #         "name": name, "mail": email, "password": passwrd, "phone": phone, "profilefill": "0"
    #     }
    #     db.child("users").child(phone).set(data)
    #
    #     return render(req, 'redirecthome.html',
    #                   {"swicon": "success", "swtitle": "Done", "swmsg": "Registration Done Successfully.",
    #                    "path": "login"})


def updatescholarhiptofire(req):
    sname = req.POST['sname']
    samt = req.POST['samt']
    scourse = req.POST['scoursename']
    scat = req.POST['scat']
    seligibility = req.POST['seligibility']

    key = req.POST['key']
    strdead = 'sdeadline-' + key
    sdeadline = req.POST[strdead]
    # logo = req.session['trustVal'].get("logo")
    trust_id = req.session['trustkey']
    db = connect_firebase()

    data = {
        "amount": samt, "course": scourse, "eligibility": seligibility, "lastdate": sdeadline,
        "level": scat, "name": sname, "trust_id": trust_id
    }

    # db.child("Scheme").child(key).update(
    #     data
    # )
    Scheme.objects.update_or_create(
            id=key,
            defaults=data
        )


    return render(req, 'redirecthome.html',
                  {"swicon": "success", "swtitle": "Done", "swmsg": "Scholarhip Updated Successfully.",
                   "path": "trusthome"})


def addscholarhiptofire(req):
    sname = req.POST['sname']
    samt = req.POST['samt']
    scourse = req.POST['scoursename']
    scat = req.POST['scat']
    seligibility = req.POST['seligibility']
    sdeadline = req.POST['sdeadline']
    timestamp = datetime.timestamp(datetime.now())
    trust_id = req.session['trustkey']
    # db = connect_firebase()

    data = {
        "amount": samt, "course": scourse, "eligibility": seligibility, "lastdate": sdeadline,
        "level": scat, "logo": "", "name": sname, "trust_id": trust_id
    }
    # print(str(timestamp))

    #     strtimestamp = str(timestamp).replace('.', '')

    # db.child("Scheme").child(strtimestamp[:13]).set(
    #     data
    # )
    Scheme.objects.create(**data)
    return render(req, 'redirecthome.html',
                  {"swicon": "success", "swtitle": "Done", "swmsg": "Scholarship Added Successfully.",
                   "path": "trusthome"})


def viewtrustdetails(request, pk):

    try:
        global schemes
        schemes = None
        db = connect_firebase()
        trust = db.child("Trust").child(str(pk)).get().val()
        trust = Trust.objects.get(trust_id=str(pk))
        all_trusts = Trust.objects.exclude(trust_id=str(pk))
        # del all_trusts[str(pk)]
        schemes = Scheme.objects.filter(trust_id=pk)

        return render(request, 'trustdetails.html',
                      {"scheme": schemes, 'trust': trust, "all_trusts": all_trusts,
                       "islog": True if 'isLogin' in request.session else False
                       })
    except:
       print("Error")
       return render(request, 'redirecthome.html',
                     {"swicon": "error", "swtitle": "Error", "swmsg": "Error", "path": ""})


def viewschemedetails(request, pk):
    global schemes
    db = connect_firebase()
    #
    # all_trusts = db.childaddtrustdb("Trust").order_by_key().get().val()
    # del all_trusts[str(pk)]
    applied_scheme = None
    isapplyscheme=False
    isapply = "False"
    if AppliedScheme.objects.filter(userid=request.session['currentUser'],scheme_id=pk).exists():
        isapply = "True"
    # try:
    #
    #     applied_scheme = request.session['currentUser'].get("applied_scheme")
    #     isapplyscheme = Scheme.objects.filter(userid=request.session['currentUser'],scheme_id=pk).exists()
    # except:
    #     pass
    # if applied_scheme == None:
    #     applied_scheme = []
    # isapply = "False"
    # if str(pk) in applied_scheme:
    #     isapply = "True"
    scheme = Scheme.objects.get(id=pk)
    trust = Trust.objects.filter(trust_id=scheme.trust_id)
    # other_schemes = db.child("Scheme").order_by_child("level").equal_to(scheme.get("level")).get().val()
    other_schemes = Scheme.objects.filter(level=scheme.level).exclude(id=pk)
    print(other_schemes)
    # del other_schemes[str(pk)]
    isclosed = False
    print(scheme.lastdate)
    deadline = datetime.strptime(scheme.lastdate, "%d-%B-%Y")
    today = datetime.now()
    if deadline < today:
        isclosed = True

    return render(request, 'schemedetails.html',
                  {"scheme": scheme, 'trust': trust,
                   "other_schemes": other_schemes, "islog": True if 'isLogin' in request.session else False,
                   "scheme_key": str(pk),
                   "isapply": isapply, "isclosed": isclosed

                   })


# User Profiles#
def profile_personalDetails(request):
    if (request.session['isLogin']):
        person=UserProfile()
        userid=request.session['currentUser']
        print(userid)
        profilefill=0

        try:
            if(UserProfile.objects.filter(phone_number=userid).exists()):
                person = UserProfile.objects.get(phone_number=userid)
                profilefill = User.objects.get(phone=userid).profilefill
                phone = User.objects.get(phone=userid).phone
                mail = User.objects.get(phone=userid).mail
                print("profilefill ", profilefill)
                if (profilefill != "100"):

                    return render(request, 'user_profileDetails.html',
                                  {"userprofile": person, "profilefill": profilefill, "phone": phone, "mail": mail
                                   })
                else:
                    return render(request, 'user_completeprofile.html',
                                  {"userprofile": person, "profilefill": profilefill, "phone": phone, "mail": mail
                                   })
            else:
                person = UserProfile()
                profilefill = User.objects.get(phone=userid).profilefill
                phone = User.objects.get(phone=userid).phone
                mail = User.objects.get(phone=userid).mail
                if (profilefill != "100"):
                    return render(request, 'user_profileDetails.html',
                                  {"userprofile": person, "profilefill": profilefill, "phone": phone, "mail": mail
                                   })
        except Exception as e:
            print(str(e))
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})

    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})


def profile_familyDetails(request):
    if (request.session['isLogin']):

        userprofile = UserProfile()
        userid = request.session['currentUser']
        profilefill=0
        try:
            if (UserProfile.objects.filter(phone_number=userid).exists()):
                userprofile = UserProfile.objects.get(phone_number=userid)
                profilefill = User.objects.get(phone=userid).profilefill
        except Exception as e:
            print(str(e))
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})

        if (profilefill != "100"):
            return render(request, 'user_familyDetails.html',
                          {"userprofile": userprofile, "profilefill": profilefill,
                           })
        else:
            return render(request, 'user_completeprofile.html',
                          {"userprofile": userprofile, "profilefill": profilefill,
                           })
    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})


def profile_education(request):
    if (request.session['isLogin']):
        userprofile = UserProfile()
        userid = request.session['currentUser']
        profilefill=0

        try:
            if (UserProfile.objects.filter(phone_number=userid).exists()):
                userprofile = UserProfile.objects.get(phone_number=userid)
                profilefill = User.objects.get(phone=userid).profilefill
        except Exception as e:
            print(str(e))
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})

        if (profilefill != "100"):
            return render(request, 'user_education.html',
                          {"userprofile": userprofile, "profilefill": profilefill})
        else:
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Profile Submitted", "swmsg": "You cant change any details",
                           "path": ""})
    else:
        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})


def profile_doc(request):
    if (request.session['isLogin']):
        userprofile = UserProfile()
        userid = request.session['currentUser']
        profilefill=0

        try:
            if (UserProfile.objects.filter(phone_number=userid).exists()):
                userprofile = UserProfile.objects.get(phone_number=userid)

                profilefill = User.objects.get(phone=userid).profilefill
                print("fill  "+profilefill)
        except Exception as e:
            print(str(e))
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})

        if (profilefill != "100"):
            return render(request, 'user_doc.html',
                          {"userprofile": userprofile, "profilefill": profilefill,
                           "config": PyConfig.config1})
        else:
            return render(request, 'user_completeprofile.html',
                          {"userprofile": userprofile, "profilefill": profilefill,
                           })
    else:

        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})


def saveuserpersonalinfo(req):
    surname = req.POST['sname']
    first_name = req.POST['fname']
    last_name = req.POST['lname']
    dob = req.POST['dob']
    age = req.POST['age1']
    gender = req.POST['gender']

    email = req.POST['email']
    phone = req.POST['phone']
    parent_phone = req.POST['parent_phone']

    religious = req.POST['religious']
    cast = req.POST['cast']
    annual_income = req.POST['anual_income']
    parent_status = req.POST['ParentStatus']

    nameinpassbook = req.POST['nameinpassbook']
    account_number = req.POST['account_number']
    bank_name = req.POST['bank_name']
    ifsc_code = req.POST['ifsc_code']
    fill = req.POST['fill']
    print("Fill ",fill)
    save_draft = req.POST['saveasdraft']

    newdata = {
        "sname": surname, "fname": first_name, "lname": last_name, "dob": dob, "age": age, "gender": gender,
        "email": email, "phone": phone, "parent_phone": parent_phone,
        "religious": religious, "cast": cast, "annual_income": annual_income,
        "account_number": account_number, "bank_name": bank_name, "ifsc_code": ifsc_code.upper(),
        "nameinpassbook": nameinpassbook, "parent_status": parent_status

    }
    userid = req.session['currentUser']
    user, created = UserProfile.objects.update_or_create(
        phone_number=userid,
        defaults=newdata
    )

    User.objects.filter(phone=phone).update(profilefill=fill)
    if save_draft == "1":
        return render(req, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Personal Details Saved Successfully.",
                       "path": ""})
    if save_draft == "0":
        return render(req, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Personal Details Saved Successfully.",
                       "path": "profile-familyDetails"})


def saveuserfamilyinfo(req):
    address = req.POST['address']
    pincode = req.POST['pincode']

    fatheralive = req.POST['fatheralive']
    fathername = req.POST['fathername']
    fatheroccupation = req.POST['father_occupation']
    # fatherincome = req.POST['father_income']
    fatherincome = 0

    motheralive = req.POST['motheralive']
    mothername = req.POST['mothername']
    motheroccupation = req.POST['mother_occupation']
    # motherincome = req.POST['mother_income']
    motherincome = 0

    totalfamilymember = req.POST['totalfamilymember']
    totalearningmember = req.POST['totalearningmember']
    family_income = req.POST['family_income']

    fill = req.POST['fill']
    save_draft = req.POST['saveasdraft']
    userid = req.session['currentUser']

    print("fill ",fill)

    newdata = {
        "address": address, "pincode": pincode,
        "fatheralive": fatheralive, "fathername": fathername, "fatheroccupation": fatheroccupation,
        "fatherincome": fatherincome,
        "motheralive": motheralive, "mothername": mothername, "motheroccupation": motheroccupation,
        "motherincome": motherincome, "totalfamilymember": totalfamilymember, "totalearningmember": totalearningmember,
        "family_income": family_income
    }
    user, created = UserProfile.objects.update_or_create(
        phone_number=userid,
        defaults=newdata
    )

    User.objects.filter(phone=userid).update(profilefill=fill)
    if save_draft == "1":
        return render(req, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Family Details Saved Successfully.",
                       "path": ""})
    if save_draft == "0":
        return render(req, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Family Details Saved Successfully.",
                       "path": "profile-education"})


def saveusereducation(req):
    collegename = req.POST['collegename']
    collegeaddress = req.POST['collegeaddress']
    collegeheadname = req.POST['collegeheadname']

    coursename = req.POST['coursename']
    courseduration = req.POST['courseduration']
    courseacademicyear = req.POST['courseacademicyear']
    lastcoursename = req.POST['lastcoursename']
    lastcourseacademicyear = req.POST['lastcourseacademicyear']

    coursefees = req.POST['coursefees']
    coursefeespaid = req.POST['coursefeespaid']
    coursefeesrequired = req.POST['coursefeesrequired']

    course1name = "SSC"
    course1board = req.POST['course1board']
    course1medium = req.POST['course1medium']
    course1marks = req.POST['course1marks']
    course1markstotal = req.POST['course1markstotal']
    course1year = req.POST['course1year']
    course1per = req.POST['course1per']

    course2name = req.POST['course2name']
    course2board = req.POST['course2board']
    course2medium = req.POST['course2medium']
    course2marks = req.POST['course2marks']
    course2markstotal = req.POST['course2markstotal']
    course2year = req.POST['course2year']
    course2per = req.POST['course2per']

    #
    # course3name = req.POST['course3name']
    # course3year = req.POST['course3year']
    # course3board = req.POST['course3board']
    # course3per = req.POST['course3per']

    achievement = req.POST['achievement']

    fill = req.POST['fill']
    save_draft = req.POST['saveasdraft']


    newdata = {
        "collegename": collegename, "collegeaddress": collegeaddress, "collegeheadname": collegeheadname,
        "coursename": coursename, "courseduration": courseduration, "courseacademicyear": courseacademicyear,
        "lastcoursename": lastcoursename, "lastcourseacademicyear": lastcourseacademicyear,

        "coursefees": coursefees, "coursefeespaid": coursefeespaid, "coursefeesrequired": coursefeesrequired,

        "course1name": course1name,
        "course1board": course1board,
        "course1medium": course1medium,
        "course1marks": course1marks,
        "course1markstotal": course1markstotal,
        "course1year": course1year,
        "course1per": course1per,

        "course2name": course2name,
        "course2board": course2board,
        "course2medium": course2medium,
        "course2marks": course2marks,
        "course2markstotal": course2markstotal,
        "course2year": course2year,
        "course2per": course2per,

        "achievement": achievement
    }
    phonekey=req.session['currentUser']
    user, created = UserProfile.objects.update_or_create(
        phone_number=phonekey,
        defaults=newdata
    )

    User.objects.filter(phone=phonekey).update(profilefill=fill)
    if save_draft == "1":
        return render(req, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Education Details Saved Successfully.",
                       "path": ""})
    if save_draft == "0":
        return render(req, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Education Details Saved Successfully.",
                       "path": "profile-uploaddoc"})


def savedocuments(req):
    docphotoidname = req.POST['docphotoidname']
    docageproofname = req.POST['docageproofname']

    docadmissionname = req.POST['docadmissionname']
    doccurrentfeename = req.POST['doccurrentfeename']

    docaddressname = req.POST['docaddressname']
    docincomename = req.POST['docincomename']

    docphotoidurl = req.POST['docphotoidurl']

    docageproofurl = req.POST['docageproofurl']

    docadmissionurl = req.POST['docadmissionurl']
    doccurrentfeeurl = req.POST['doccurrentfeeurl']
    docaddressurl = req.POST['docaddressurl']
    docincomeurl = req.POST['docincomeurl']

    doccourse1url = req.POST['doccourse1url']
    doccourse2url = req.POST['doccourse2url']
    docpassbookurl = req.POST['docpassbookurl']

    fill = req.POST['fill']
    save_draft = req.POST['saveasdraft']

    db = connect_firebase()

    newdata = {
        "docphotoidname": docphotoidname, "docageproofname": docageproofname, "docadmissionname": docadmissionname,
        "doccurrentfeename": doccurrentfeename, "docaddressname": docaddressname, "docincomename": docincomename,
        "docphotoidurl": docphotoidurl, "docageproofurl": docageproofurl, "docadmissionurl": docadmissionurl,
        "doccurrentfeeurl": doccurrentfeeurl,
        "docaddressurl": docaddressurl, "docincomeurl": docincomeurl, "doccourse1url": doccourse1url,
        "doccourse2url": doccourse2url, "docpassbookurl": docpassbookurl
    }
    phonekey=req.session['currentUser']

    user, created = UserProfile.objects.update_or_create(
        phone_number=phonekey,
        defaults=newdata
    )

    User.objects.filter(phone=phonekey).update(profilefill=fill)
    if save_draft == "1":
        return render(req, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Documents Saved Successfully.",
                       "path": ""})
    if save_draft == "0":
        return render(req, 'redirecthome.html',
                      {"swicon": "success", "swtitle": "Done", "swmsg": "Profile Submitted Successfully.",
                       "path": "user-completeprofile"})


def user_completeprofile(request):
    if (request.session['isLogin']):
        userprofile = UserProfile()
        userphone = request.session['currentUser']


        try:
            if (UserProfile.objects.filter(phone_number=userphone).exists()):
                userprofile = UserProfile.objects.get(phone_number=userphone)
        except Exception as e:
            print(str(e))
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})

        if User.objects.get(phone=request.session['currentUser']).profilefill == "100":
            return render(request, 'user_completeprofileform.html',
                          {"userprofile": userprofile, "currentuser": request.session['currentUser'],
                           })
        else:
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Profile Not Submitted", "swmsg": "Please Complete profile",
                           "path": ""})
    else:

        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})


# Apply for scheme/scholarship

def applyscholarship(request):  # user has click on apply button add userinfo to db
    if (request.session['isLogin']):
        # userprofile = OrderedDict()
        print(request.session['currentUser'])
        # userprofile = UserProfile.objects.get(phone_number=request.session['currentUser'])

        # db = connect_firebase()
        #
        # request.session['currentUser'] = db.child("users").child(
        #     request.session['currentUser'].get("phone")).get().val()
        # try:
        #     userprofile = db.child("UserProfile").child(request.session['currentUser'].get("phone")).get().val()
        # except:
        #     print("Error")

        if User.objects.get(phone=request.session['currentUser']).profilefill == "100":

            userprofile = UserProfile.objects.get(phone_number=request.session['currentUser'])
            schemeid = request.POST['schemeid_apply']
            amount = request.POST['amount']
            trust_id = request.POST['trust_id']
            schemename = request.POST['schemename']
            userphone = request.session['currentUser']
            name = userprofile.sname + " " + userprofile.fname+ " " + userprofile.lname
            status = "Pending"

            applicationid = datetime.timestamp(datetime.now())
            applicationid = str(applicationid).replace('.', '')
            applicationid = applicationid[:13]

            # tname = db.child("Trust").child(trust_id).child("name").get().val()
            tname = Trust.objects.get(trust_id=trust_id).name
            print(tname)

            data = {
                "userid": userphone, "username": name,
                "scheme_id": schemeid, "scheme_name": schemename, "schemeamount": amount,
                "status": status, "remark": "", "sanctionedamount": "0", "trust_id": trust_id, "tname": tname,
                "applicationid":applicationid
            }

            AppliedScheme.objects.create(**data)


            return render(request, 'redirecthome.html',
                          {"swicon": "success", "swtitle": "Done",
                           "swmsg": "Applied Successfully. Your Application number is " + applicationid,
                           "path": "appliedscholarship"})
        else:
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Profile Not Submitted", "swmsg": "Please Complete profile",
                           "path": "profile-personalDetails"})
    else:

        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})


def appliedscholarship(request):
    if (request.session['isLogin']):
        data = AppliedScheme.objects.filter(userid=request.session['currentUser']).values()

        # db = connect_firebase()
        # try:
        #     data = db.child("AppliedScheme").order_by_child("userid").equal_to(
        #         request.session['currentUser'].get("phone")).get().val()
        # except:
        #     pass

        return render(request, 'user_appliedscheme.html',
                      {"currentuser": request.session['currentUser'], "applied_schemes": data})
    else:

        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})


# importing the necessary libraries
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string


# defining the function to convert an HTML file to a PDF file
def html_to_pdf(template_src, context_dict={"Name": "AADDAD"}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def pdf_form(request):
    open('Scholar_Help/templates/temp.html', "w").write(render_to_string('result.html', {'data': {"Name": "AADDAD"}}))
    pdf = html_to_pdf('result.html', {"Name": "Sohil"})

    # rendering the template
    return HttpResponse(pdf, content_type='application/pdf')


def html_form(request):
    if (request.session['isLogin']):

        try:
            # userprofile = db.child("UserProfile").child(request.session['currentUser'].get("phone")).get().val()
            userprofile = UserProfile.objects.get(phone_number=request.session['currentUser'])
            user = User.objects.get(phone=request.session['currentUser'])
        except:
            print("Error")

        if user.profilefill == "100":
            return render(request, 'result.html',
                          {"userprofile": userprofile, "currentuser": request.session['currentUser'],
                           })
        else:
            return render(request, 'redirecthome.html',
                          {"swicon": "error", "swtitle": "Profile Not Submitted", "swmsg": "Please Complete profile",
                           "path": ""})
    else:

        return render(request, 'redirecthome.html',
                      {"swicon": "error", "swtitle": "Error", "swmsg": "Please try again", "path": "login"})
