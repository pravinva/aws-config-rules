#This file made available under CC0 1.0 Universal (https://creativecommons.org/publicdomain/zero/1.0/legalcode)
#
# RULE DESCRIPTION
# This example rule checks that EC2 instances are EBS optimized (optionally checks that ebsOptimized field is
# equal to value passed in parameter)
#
# RULE DETAILS
# Trigger Type (Change Triggered or Periodic: Change Triggered
# If Changed Triggered, add Scope of Changes e.g. ["AWS::EC2::Instance"] or ["AWS::EC2::Instance","AWS::EC2::InternetGateway"]
# If Periodic, add Scope of Changes e.g. ["AWS::::Account"] 
APPLICABLE_RESOURCES = ["AWS::IAM::User"]

# Required Parameters: None
# Optional Parameter: Parameter1 
# Optional Parameter value example : True

import json
import boto3
import datetime
from datetime import date
import dateutil
from dateutil import parser

aws_config = boto3.client('config')



def is_non_compliant(configuration_item, rule_parameters):
    userName     =  configuration_item['configuration']['userName']
    grouplist    =  configuration_item['configuration']['groupList']
    createDate   =  dateutil.parser.parse(configuration_item['configuration']['createDate'])
    created_date = date(createDate.year, createDate.month, createDate.day)
    current_date = date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
    age = (current_date - created_date).days
    
    for item in grouplist:
        if (item.startswith('Time_Limit')):
           expiration = item.split('_')[2]
           if  age > int(expiration):
               return True
           else:
               return False
 
def evaluate_compliance(configuration_item, rule_parameters):
    if is_not_applicable(configuration_item, rule_parameters):
        return 'NOT_APPLICABLE'
    elif is_non_compliant(configuration_item, rule_parameters):
    else:
        return 'COMPLIANT'

def is_not_applicable(configuration_item, rule_parameters):
    return configuration_item["resourceType"] not in APPLICABLE_RESOURCES


def lambda_handler(event, context):
    
    invokingEvent = json.loads(event['invokingEvent'])
    ruleParameters = json.loads(event['ruleParameters'])
    configuration_item  = invokingEvent["configurationItem"]

    compliance = 'NOT_APPLICABLE'
    compliance = evaluate_compliance(configuration_item, ruleParameters)
    # Put together the request that reports the evaluation status
    evaluations = [{
            'ComplianceResourceType': configuration_item['resourceType'],
            'ComplianceResourceId': configuration_item['resourceId'],
            'ComplianceType': compliance,
            'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
    }]
    resultToken = event['resultToken']
    
