import json
import pytest
import synapseclient
from send_budget_alert import app

@pytest.fixture()
def sns_event():
    """ Generates SNS Event"""

    return {
      "Records": [
        {
          "EventVersion": "1.0",
          "EventSubscriptionArn": "arn:aws:sns:us-east-2:123456789012:sns-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
          "EventSource": "aws:sns",
          "Sns": {
              "Type" : "Notification",
              "MessageId" : "790b30bd-2a13-58f4-b0fb-672c044b52ef",
              "TopicArn" : "arn:aws:sns:us-east-1:465877038949:lambda-budgets-BudgetMakerNotificationTopic-1G7CL03USSYRY",
              "Subject" : "test message",
              "Message" : "test test",
              "Timestamp" : "2020-07-21T17:55:36.052Z",
              "SignatureVersion" : "1",
              "Signature" : "p/JfHLzBNjqhZ7/PcghK05NRqiIYbQtVQa/47FxH0tV2altKjKqGMTbr2gya17NQVKxkoZTDpmzBf7Ho+JzVbWLb03jQXuFUquidASIlNhJNwy7T72g9IdRX1g2FI4HT9iaM7Dh9hQAbsMVsYsVNtPGz+s1itbrBInio2YIjuGEitPFBpMH55vHSl0IMeavGpO0MBQvLWPWCRPqtsugoj9s/h3PbAmLoL7gHKEUdnCjCSXzdxcM7f11dUMl0uMPjrAB0BT0BaTVzTFmdWDq9l1MX3I6F5GhYgDoln7dR7KZiQBc1k/90t/Iw8vv0fme9JogsB2JUgrwqOSwE/FZPBQ==",
              "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem",
              "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:465877038949:lambda-budgets-BudgetMakerNotificationTopic-1G7CL03USSYRY:709a067a-a7ca-4765-9ad5-a85844aa9310",
              "MessageAttributes" : {
                "SynapseId" : {"Type":"String","Value":"3388489"}
              }
            }
        }
      ]
    }


def test_lambda_handler(sns_event, mocker):
    # mock synapse client
    MockSynapse = mocker.patch('synapseclient.Synapse')
    mock_synapse_client = MockSynapse.return_value
    
    # mock the environment
    mocker.patch.dict('os.environ', {'SYNAPSE_USER_NAME': 'username', 'SYNAPSE_PASSWORD': 'password'})
    
    # method under test
    ret = app.lambda_handler(sns_event, "")

    # check that synapse_client.login() was called with 'username', 'password'
    mock_synapse_client.login.assert_called_once_with('username', 'password')

    # check that synapse_client.sendMessage() was called correctly
    mock_synapse_client.sendMessage.assert_called_once_with(["3388489"], "test message", "test test", "text/plain")
    
    # check error code
    assert ret["errorCode"] == 0
    assert ret["errorMessage"] is None
    
@pytest.fixture()
def bad_sns_event_no_syn_id():
    """ Generates SNS Event"""

    return {
      "Records": [
        {
          "EventVersion": "1.0",
          "EventSubscriptionArn": "arn:aws:sns:us-east-2:123456789012:sns-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
          "EventSource": "aws:sns",
          "Sns": {
              "Type" : "Notification",
              "MessageId" : "790b30bd-2a13-58f4-b0fb-672c044b52ef",
              "TopicArn" : "arn:aws:sns:us-east-1:465877038949:lambda-budgets-BudgetMakerNotificationTopic-1G7CL03USSYRY",
              "Subject" : "test message",
              "Message" : "test test",
              "Timestamp" : "2020-07-21T17:55:36.052Z",
              "SignatureVersion" : "1",
              "Signature" : "p/JfHLzBNjqhZ7/PcghK05NRqiIYbQtVQa/47FxH0tV2altKjKqGMTbr2gya17NQVKxkoZTDpmzBf7Ho+JzVbWLb03jQXuFUquidASIlNhJNwy7T72g9IdRX1g2FI4HT9iaM7Dh9hQAbsMVsYsVNtPGz+s1itbrBInio2YIjuGEitPFBpMH55vHSl0IMeavGpO0MBQvLWPWCRPqtsugoj9s/h3PbAmLoL7gHKEUdnCjCSXzdxcM7f11dUMl0uMPjrAB0BT0BaTVzTFmdWDq9l1MX3I6F5GhYgDoln7dR7KZiQBc1k/90t/Iw8vv0fme9JogsB2JUgrwqOSwE/FZPBQ==",
              "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem",
              "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:465877038949:lambda-budgets-BudgetMakerNotificationTopic-1G7CL03USSYRY:709a067a-a7ca-4765-9ad5-a85844aa9310",
              "MessageAttributes" : {
              }
            }
        }
      ]
    }

def test_lambda_handler_bad_event(bad_sns_event_no_syn_id, mocker):
    # mock synapse client
    MockSynapse = mocker.patch('synapseclient.Synapse')
    mock_synapse_client = MockSynapse.return_value
    
    # mock the environment
    mocker.patch.dict('os.environ', {'SYNAPSE_USER_NAME': 'username', 'SYNAPSE_PASSWORD': 'password'})
    
    # method under test
    ret = app.lambda_handler(bad_sns_event_no_syn_id, "")

    # check that synapse_client.login() was called with 'username', 'password'
    mock_synapse_client.login.assert_called_once_with('username', 'password')

    # check that synapse_client.sendMessage() was not called
    mock_synapse_client.sendMessage.assert_not_called()
    
    # check error code
    assert ret["errorCode"] == 1
    assert ret["errorMessage"] is not None
