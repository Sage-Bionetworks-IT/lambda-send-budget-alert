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
          "EventSubscriptionArn":
          "arn:aws:sns:us-east-2:123456789012:sns-lambda:26",
          "EventSource": "aws:sns",
          "Sns": {
              "Type": "Notification",
              "MessageId": "790b30bd-2a13-58f4-b0fb-672c044b52ef",
              "TopicArn":
              "arn:aws:sns:us-east-1:465877038949:lambda-budgets-BudgetYRY",
              "Subject": "AWS Budgets: service-catalog_3388489 ...hold",
              "Message": "test test",
              "Timestamp": "2020-07-21T17:55:36.052Z",
              "SignatureVersion": "1",
              "Signature":
              "p/JfHLzBNjqhZ7/iQBc1k/90t/Iw8vv0fme9JogsB2JUgrwqOSwE/FZPBQ==",
              "SigningCertURL":
              "https://sns.us-east-1.amazonaws.com/Sce-a86b6.pem",
              "UnsubscribeURL":
              "https://sns.us-east-1.amazonaws.com/?Action=Unsubscrda-310",
              "MessageAttributes": {
              }
            }
        }
      ]
    }


def test_parse_user_id_from_subject():
    # Happy case
    assert "1234567" == app.parse_user_id_from_subject(
        "AWS Budgets: service-catalog_1234567 ...hold")

    # Check that it doesn't match some other number
    assert "1234567" == app.parse_user_id_from_subject(
        "AWS 9876 Budgets: service-catalog_1234567 ... 54321 hold")

    # Check that various invalid cases correctly return None
    assert app.parse_user_id_from_subject("") is None

    assert app.parse_user_id_from_subject(None) is None

    assert app.parse_user_id_from_subject(
        "AWS Budgets: service-catalog_NotANumber foo") is None

    assert app.parse_user_id_from_subject(
        "...catalog_1234567 ...hold") is None


def test_lambda_handler(sns_event, mocker):
    # mock synapse client
    MockSynapse = mocker.patch('synapseclient.Synapse')
    mock_synapse_client = MockSynapse.return_value

    # mock the environment
    mocker.patch.dict('os.environ',
                      {'SYNAPSE_USER_NAME': 'username',
                       'SYNAPSE_PASSWORD': 'password'})

    # method under test
    ret = app.lambda_handler(sns_event, "")

    # check that synapse_client.login() was called with 'username', 'password'
    mock_synapse_client.login.assert_called_once_with('username', 'password')

    # check that synapse_client.sendMessage() was called correctly
    mock_synapse_client.sendMessage.assert_called_once_with(
            ["3388489"], "AWS Budgets: service-catalog_3388489 ...hold",
            "test test", "text/plain")

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
          "EventSubscriptionArn":
          "arn:aws:sns:us-east-2:123456789012:sns-lambda:21b6",
          "EventSource": "aws:sns",
          "Sns": {
              "Type": "Notification",
              "MessageId": "790b30bd-2a13-58f4-b0fb-672c044b52ef",
              "TopicArn":
              "arn:aws:sns:us-east-1:465877038949:lambda-budgets-BudgetYRY",
              "Subject": "test message",
              "Message": "test test",
              "Timestamp": "2020-07-21T17:55:36.052Z",
              "SignatureVersion": "1",
              "Signature":
              "p/JfHLzBNjqhZ7/iQBc1k/90t/Iw8vv0fme9JogsB2JUgrwqOSwE/FZPBQ==",
              "SigningCertURL":
              "https://sns.us-east-1.amazonaws.com/Sice-a86b6.pem",
              "UnsubscribeURL":
              "https://sns.us-east-1.amazonaws.com/?Action=Unsubscrda-310"
          }
        }
      ]
    }


def test_lambda_handler_bad_event(bad_sns_event_no_syn_id, mocker):
    # mock synapse client
    MockSynapse = mocker.patch('synapseclient.Synapse')
    mock_synapse_client = MockSynapse.return_value

    # mock the environment
    mocker.patch.dict('os.environ',
                      {'SYNAPSE_USER_NAME': 'username',
                       'SYNAPSE_PASSWORD': 'password'})

    # method under test
    ret = app.lambda_handler(bad_sns_event_no_syn_id, "")

    # check that synapse_client.login() was called with 'username', 'password'
    mock_synapse_client.login.assert_called_once_with('username', 'password')

    # check that synapse_client.sendMessage() was not called
    mock_synapse_client.sendMessage.assert_not_called()

    # check error code
    assert ret["errorCode"] == 1
    assert ret["errorMessage"] is not None
