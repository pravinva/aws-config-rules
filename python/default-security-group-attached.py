 # This file made available under CC0 1.0 Universal (https://creativecommons.org/publicdomain/zero/1.0/legalcode)
 #
 # Description: Check that default security groups are not attached to EC2
 # Trigger Type: Change Triggered
 # Scope of Changes: EC2:NetworkInterface
 # Accepted Parameters: None
 # Your Lambda function execution role will need to have a policy that provides the appropriate
 # permissions.  Here is a policy that you can consider.  You should validate this for your own
 # environment
 #{
 #    "Version": "2012-10-17",
 #    "Statement": [
 #        {
 #            "Effect": "Allow",
 #            "Action": [
 #                "logs:CreateLogGroup",
 #                "logs:CreateLogStream",
 #                "logs:PutLogEvents"
 #            ],
 #            "Resource": "arn:aws:logs:*:*:*"
 #        },
 #        {
 #            "Effect": "Allow",
 #            "Action": [
 #                "config:PutEvaluations",
 #                "ec2:DescribeNetworkInterfaces"
 #            ],
 #            "Resource": "*"
 #        }
 #    ]
 #}


 import boto3
 import json

 APPLICABLE_RESOURCES = ["AWS::EC2::NetworkInterface"]

 def evaluate_compliance(configuration_item):

     # Start as compliant
     compliance_type = 'COMPLIANT'
     annotation = "Resource is compliant."

     # Check resource for applicability
     if configuration_item["resourceType"] not in APPLICABLE_RESOURCES:
         compliance_type = 'NOT_APPLICABLE'
         annotation = "The rule doesn't apply to resources of type " \
                      + configuration_item["resourceType"] + "."

     # Iterate over security groups
     for sg in configuration_item['configuration']['groups']:
         if  sg['groupName'] == 'default':
             compliance_type = 'NON_COMPLIANT'
             annotation = 'Default security group ' \
                          'is attached to ' \
                          + configuration_item['configuration']['privateIpAddress']
             break

     return {
         "compliance_type": compliance_type,
         "annotation": annotation
     }

def lambda_handler(event, context):

     invoking_event = json.loads(event['invokingEvent'])
     configuration_item = invoking_event["configurationItem"]
     evaluation = evaluate_compliance(configuration_item)
     config = boto3.client('config')

     print('Compliance evaluation for %s: %s' % (configuration_item['resourceId'], evaluation["compliance_type"]))
     print('Annotation: %s' % (evaluation["annotation"]))

     response = config.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': invoking_event['configurationItem']['resourceType'],
                'ComplianceResourceId':   invoking_event['configurationItem']['resourceId'],
                'ComplianceType':         evaluation["compliance_type"],
                "Annotation":             evaluation["annotation"],
                'OrderingTimestamp':      invoking_event['configurationItem']['configurationItemCaptureTime']
            },
        ],
        ResultToken=event['resultToken'])

