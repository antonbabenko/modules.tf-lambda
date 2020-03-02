# #!/usr/bin/env pytest
#
# from json import loads
# from os import environ
#
# import pytest
# from modulestf.cloudcraft.graph import populate_graph
#
# events = (
#     (
#       {
#         "AlarmType": "Unsupported alarm type",
#         "AWSAccountId": "000000000000",
#         "NewStateValue": "ALARM",
#       }
#     ),
#     (
#       {
#         "Records": [
#           {
#             "EventSource": "aws:sns",
#             "EventVersion": "1.0",
#             "EventSubscriptionArn": "arn:aws:sns:OMITTED:OMITTED:slack-notification:15405ea9-77dc-40d4-ba55-3f87997e5abb",
#             "Sns": {
#               "Type": "Notification",
#               "MessageId": "7c9f6458-2b6c-55f4-aee9-3222e6745e5a",
#               "TopicArn": "arn:aws:sns:OMITTED:OMITTED:slack-notification",
#               "Subject": "RDS Notification Message",
#               "Message": "{\"Event Source\":\"db-snapshot\",\"Event Time\":\"2019-12-23 14:10:24.176\",\"IdentifierLink\":\"https://console.aws.amazon.com/rds/home?region=OMITTED#snapshot:id=MY-TEST\"}",
#               "Timestamp": "2019-12-23T14:10:32.199Z",
#               "SignatureVersion": "1",
#               "Signature": "kPGKHJ9rWTgK0Lw/UJow59z4B6cjoPfbnYlwDCbO/Wk/IlPmqjQMib94+GqozIPw4F9QEwwzb7RyaQ4IC3/iBoPYM5shVXkxdl2I8a7fyYqer4QgJWCUijZ60HhYZ7m2WeO7NJei5/8ahtLtyIPoD+8rHNiGJ9JV2RXokdsgWzbXIhbsQ6xGmcbwNe5FkpiqTcw7/52uJUWyUUcRz1E/BZEC5kFAw///u8JlioRmIC95e0isq724+5hf3BEryab3HC+5+BlWMPGug4FQ8kS8rquiXLKTl/e4ubFqz1GEUjiNoNXHqOqm9Bq+WNcBrmKMGNGhzr6In8Kh4srr56oGfQ==",
#               "SigningCertUrl": "https://sns.OMITTED.amazonaws.com/SimpleNotificationService-6aad65c2f9911b05cd53efda11f913f9.pem",
#               "UnsubscribeUrl": "https://sns.OMITTED.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:OMITTED:OMITTED:slack-notification:15405ea9-77dc-40d4-ba55-3f87997e5abb",
#               "MessageAttributes": {}
#             }
#           }
#         ]
#       }
#     )
# )
#
#
# @pytest.fixture(scope='module', autouse=True)
# def check_environment_variables():
#     required_environment_variables = ("AA")
#     missing_environment_variables = []
#     for k in required_environment_variables:
#         if k not in environ:
#             missing_environment_variables.append(k)
#
#     if len(missing_environment_variables) > 0:
#         pytest.exit('Missing environment variables: {}'.format(", ".join(missing_environment_variables)))
#
#
# @pytest.mark.parametrize("event", events)
# def test_cloudcraft_graph(event):
#     # if 'Records' in event:
#     #     response = notify_slack.lambda_handler(event, 'self-context')
#     #
#     # else:
#     file = open(event, 'r')
#     data = json.load(file)
#
#     graph = populate_graph(data)
#
#     # response = loads(response)
#     assert graph is not False
