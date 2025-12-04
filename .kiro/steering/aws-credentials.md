# AWS Credentials

When working with AWS services (S3, DynamoDB, Lambda, etc.), always use the credentials from `.aws-temp-creds.sh`.

## Usage

Before running any AWS CLI commands or CDK operations, source the credentials file:

```bash
source .aws-temp-creds.sh
```

Or inline with commands:

```bash
source .aws-temp-creds.sh && aws s3 ls
source .aws-temp-creds.sh && cdk deploy
```

## Important Notes

- The credentials file is in `.gitignore` and should never be committed
- These are temporary credentials that may expire
- Always check if credentials are valid before running AWS operations
- The account ID is: 509399592822
- The default region is: us-west-2
