import json
import random

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from web.models import  AppliedScheme


def savejson(req):
    with open("demojson.json", "r") as file:
        # Load the JSON data from the file
        json_data = json.load(file)

    for key,item in json_data.items():
        try:
            # Attempt to get an existing object with the same name
            appliedScheme = AppliedScheme.objects.get(applicationid=key)
            # Update the object's fields
            appliedScheme.applicationid = key
            appliedScheme.scheme_id = item.get('scheme_id', '')
            appliedScheme.scheme_name = item.get('scheme_name', '')
            appliedScheme.tname = item.get('tname', '')
            appliedScheme.trust_id = item.get('trust_id', '')
            appliedScheme.userid = item.get('userid', '')
            appliedScheme.username = item.get('username', '')
            appliedScheme.status = item.get('status', '')
            appliedScheme.schemeamount = item.get('schemeamount', '')
            appliedScheme.sanctionedamount = item.get('sanctionedamount', '')
            appliedScheme.interviewdate = item.get('interviewdate', '')
            appliedScheme.remark = item.get('remark', '')

            appliedScheme.save()
        except ObjectDoesNotExist:
            # Create a new object if one doesn't already exist

            appliedScheme = AppliedScheme(
                applicationid=key,
                scheme_id=item.get('scheme_id', ''),
                scheme_name=item.get('scheme_name', ''),
                tname=item.get('tname', ''),
                trust_id=item.get('trust_id', ''),
                userid=item.get('userid', ''),
                username=item.get('username', ''),
                status=item.get('status', ''),
                schemeamount=item.get('schemeamount', ''),
                sanctionedamount=item.get('sanctionedamount', ''),
                interviewdate=item.get('interviewdate', ''),
                remark=item.get('remark', ''),

            )
        # Save the object to the database
        appliedScheme.save()
    return HttpResponse("Done!")