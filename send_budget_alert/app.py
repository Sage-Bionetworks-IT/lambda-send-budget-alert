import json
import synapseclient
import re
import os
import logging
import boto3
from botocore.exceptions import ClientError

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

BUDGET_NAME_PREFIX = 'service-catalog_'

USER_ID_PATTERN = re.compile(f'{BUDGET_NAME_PREFIX}(\\d+)')


def parse_user_id_from_subject(s):
    '''
    Looks in the passed string for 'service-catalog_123456'
    and parses out the '123456' which is the Synapse user id

    returns None if the input is not in this format
    '''
    if s is None:
        return None

    result = USER_ID_PATTERN.search(s)

    if result is None:
        return None
    else:
        return result.group(1)

SSM_ERROR_PREFIX = 'secret not found in AWS System Manager parameter store'
MISSING_ENVIRONMENT_VARIABLE_MESSAGE = 'Environment variable is required'


def get_ssm_parameter(key_name):
    return boto3.client('ssm').get_parameter(
      Name=key_name,
      WithDecryption=True)

def get_ssm_secret(key_name):
  '''Retrieve a secret from AWS System Manager'''
  try:
    response = get_ssm_parameter(key_name)
  except ClientError as e:
    client_error_msg = e.response['Error']['Code']
    exception_msg = f'{SSM_ERROR_PREFIX}: key_name={key_name}; {client_error_msg}'
    raise Exception(exception_msg)

  return response['Parameter']['Value']


def get_variables(func, var_names, error_msg):
  '''Generic method to extract values and raise error if they are missing'''
  values = []

  for var_name in var_names:
    value = func(var_name)
    if not value:
      raise ValueError(f'{error_msg}: {var_name}')
    values.append(value)

  return values


def get_envvars():
  '''Extract environment variables'''
  env_var_names = [
    'SYNAPSE_USER_KEYNAME',
    'SYNAPSE_PASSWORD_KEYNAME'
  ]
  return get_variables(os.getenv, env_var_names, MISSING_ENVIRONMENT_VARIABLE_MESSAGE)


def lambda_handler(event, context):
    """
    Parameters
    ----------
    event: dict, required
        https://docs.aws.amazon.com/lambda/latest/dg/with-sns.html
        We use two fields from each record:
        (1) 'subject' the notification subject
        (2) 'message' this is the notification to forward

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
        synapse_user_key_name, synapse_password_key_name  = get_envvars()
        synapse_user_name = get_ssm_secret(synapse_user_key_name)
        synapse_password = get_ssm_secret(synapse_password_key_name)
        # Lambda only allows writing to /tmp.  Omitting this results in: [Errno 30] Read-only file system: ‘/home/sbx_user...’
        synapseclient.core.cache.CACHE_ROOT_DIR = '/tmp/.synapseCache'
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
        log.error(ex, exc_info=True)
        errorCode = 1
        errorMessage = str(ex)

    return {
        "errorCode": errorCode,
        "errorMessage": errorMessage
    }
