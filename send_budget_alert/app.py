import json
import synapseclient
import re
import os

USER_ID_PATTERN = re.compile("service-catalog_(\\d+)")


def parse_user_id_from_subject(s):
    if s is None:
        return None

    result = USER_ID_PATTERN.search(s)

    if result is None:
        return None
    else:
        return result.group(1)


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
            userId = parse_user_id_from_subject(subject)
            if userId is None:
                raise ValueError("No user id in "+subject)
            # send email
            # https://python-docs.synapse.org/build/html/Client.html#synapseclient.Synapse.sendMessage
            synapse_client.sendMessage(
                [userId], subject,
                message, "text/plain")
    except Exception as ex:
        # Send some context about this error to Lambda Logs
        print(ex)
        errorCode = 1
        errorMessage = str(ex)

    return {
        "errorCode": errorCode,
        "errorMessage": errorMessage
    }
