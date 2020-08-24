# lambda-send-budget-alert
A Lambda that listens to an SNS topic and forwards notifications to Synapse users by email.
This works in conjunction with https://github.com/Sage-Bionetworks-IT/lambda-budgets,
which generates alerts and sends them to SNS. Since AWS Budgets cannot email Synapse users,
it instead publishes the notifications to SNS, after which this lambda converts them to
email notifications.

### Contributions
Contributions are welcome.

### Requirements
Run `pipenv install --dev` to install both production and development
requirements, and `pipenv shell` to activate the virtual environment. For more
information see the [pipenv docs](https://pipenv.pypa.io/en/latest/).

After activating the virtual environment, run `pre-commit install` to install
the [pre-commit](https://pre-commit.com/) git hook.

### Create a local build

```shell script
$ sam build --use-container
```

### Run locally

```shell script
$ sam local invoke SendBudgetAlertFunction --event events/event.json
```

### Run unit tests
Tests are defined in the `tests` folder in this project. Use PIP to install the
[pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```shell script
$ python -m pytest tests/ -v
```

## Deployment

### Build

```shell script
sam build
```

## Deploy Lambda to S3
This requires the correct permissions to upload to bucket
`bootstrap-awss3cloudformationbucket-19qromfd235z9` and
`essentials-awss3lambdaartifactsbucket-x29ftznj6pqw`

```shell script
sam package --template-file .aws-sam/build/template.yaml \
  --s3-bucket essentials-awss3lambdaartifactsbucket-x29ftznj6pqw \
  --output-template-file .aws-sam/build/lambda-send-budget-alert.yaml

aws s3 cp .aws-sam/build/lambda-send-budget-alert.yaml s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/lambda-send-budget-alert/master/
```

## Install Lambda into AWS
Create the following [sceptre](https://github.com/Sceptre/sceptre) file

config/prod/lambda-send-budget-alert.yaml
```yaml
template_path: "remote/lambda-send-budget-alert.yaml"
stack_name: "lambda-send-budget-alert"
parameters:
  SynapseUserKeyName: '/lambda-send-budget-alert/synapse-username'
  SynapsePasswordKeyName: '/lambda-send-budget-alert/synapse-password'
stack_tags:
  Department: "Platform"
  Project: "Infrastructure"
  OwnerEmail: "it@sagebase.org"
hooks:
  before_launch:
    - !cmd "curl https://s3.amazonaws.com/bootstrap-awss3cloudformationbucket-19qromfd235z9/lambda-send-budget-alert/master/lambda-send-budget-alert.yaml --create-dirs -o templates/remote/lambda-send-budget-alert.yaml"
```

Install the lambda using sceptre:
```shell script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/lambda-send-budget-alert.yaml
```

## Set Synapse credentials in SSM

Put in SSM the credentials for the Synapse service account used to send out email notifications.  Note that the names
for the two secrets must match the names used in the Scepter file, described above.

```
aws ssm put-parameter \
--name /lambda-send-budget-alert/synapse-username \
--value "my-synapse-username" \
--type "SecureString"

aws ssm put-parameter \
--name /lambda-send-budget-alert/synapse-password \
--value "my-synapse-password" \
--type "SecureString"

```

## Author

brucehoff
