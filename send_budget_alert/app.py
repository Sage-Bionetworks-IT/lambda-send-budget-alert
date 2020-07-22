import json
import synapseclient
import re
import os


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        https://docs.aws.amazon.com/lambda/latest/dg/with-sns.html
        We use three fields from each record:
        (1) 'subject' the notification subject
        (2) 'message' this is the notification to forward
        (3) MessageAttributes.SynapseId.Value the Synapse user Id

    context: object
        Lambda Context runtime methods and attributes

    Returns
    ------
    JSON map with keys:
        errorCode: 0 if no error, non-zero otherwise
        errorMessage: describes error if errorCode is not 0
    """

    errorCode = 0
    errorMessage = None
    try:
        synapse_user_name = os.getenv("SYNAPSE_USER_NAME")
        synapse_password = os.getenv("SYNAPSE_PASSWORD")
        synapse_client = synapseclient.Synapse()
        synapse_client.login(synapse_user_name, synapse_password)
        for record in event["Records"]:
            sns = record["Sns"]
            subject = sns["Subject"]
            message = sns["Message"]
            attrs = sns["MessageAttributes"]
            userId = attrs["SynapseId"]["Value"]
            # send email
            # https://python-docs.synapse.org/build/html/Client.html#synapseclient.Synapse.sendMessage
            userIds = [userId]
            messageSubject = subject
            messageBody = message
            contentType = "text/plain"  # could be set to "text/html"
            synapse_client.sendMessage(
                userIds, messageSubject,
                messageBody, contentType)
    except Exception as ex:
        # Send some context about this error to Lambda Logs
        print(ex)
        errorCode = 1
        errorMessage = str(ex)

    return {
        "errorCode": errorCode,
        "errorMessage": errorMessage
    }
