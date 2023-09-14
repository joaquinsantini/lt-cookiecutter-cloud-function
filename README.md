# Cloud Function Cookiecutter - A cookiecutter for creating a GCP cloud function source folder

[<img src="https://img.shields.io/static/v1?label=&message=Python&color=blueviolet" />](https://github.com/topics/python)

## Table of Contents
- [What Is Cookiecutter](#what-is-cookiecutter)
- [How to Use It](#how-to-use-it)
- [Cloud Function Name](#cloud-function-name)
- [Cloud Function Description](#cloud-function-description)
- [Memory](#memory)
- [Timeout](#timeout)
- [Set Secrets](#set-secrets)
- [Set Environment Variables](#set-environment-variables)
- [Trigger Bucket](#trigger-bucket)
- [Snowflake Flag](#snowflake-flag)

## What Is Cookiecutter?

Cookiecutter is a module to automate the creation of projects based on templates. You can find the official site in [this](https://www.cookiecutter.io/) link.

You need to install cookiecutter to start using this cloud function template:

```bash
pip3 install cookiecutter
```

## How to Use It

You need to call the cookiecutter in the folder you want to create your new cloud function so for this example lets assume you cloned this repo on your Desktop:

```bash
cd Desktop/data-engineering-pipelines/cloud-functions
```

Now you are ready to create the new cloud function:

```bash
cookiecutter Desktop/data-engineering-pipelines/tools/cloud-function-cookiecutter
```

You will be asked to complete the required fields such as:
- Cloud Function Name
- Cloud Function Description
- Memory
- Timeout
- Set Secrets
- Set Environment Variables
- Trigger Bucket
- Snowflake Flag

When you finish the completion of the fields, the cookiecutter will create a new folder with the below files:
- main.py: the entry point for your cloud function
- requirements.txt: the dependencies your cloud function needs
- deploy.yaml: the configuration of the cloud function
- .env: the file containing the environment variables (and secrets) your cloud function needs

## Cloud Function Name

This will be the name for your new cloud function so a folder with that name will be created with the source code for you.

The cloud function name must be unique so if another cloud function exists with the same name, the cookiecutter will fail and it won't create the new folder.

## Cloud Function Description

This will be the description for your new cloud function. If you leave this in blank, the default description will be the name of the cloud function.

## Memory

This will be the memory allowed for the function in GCP. This value is optional (the default value is 256Mb). For more information you can visit [this](https://cloud.google.com/functions/docs/configuring/memory) link.

## Timeout

This will be the timeout for the function in GCP. This value is optional (the default value is 60s). For more information you can visit [this](https://cloud.google.com/functions/docs/configuring/timeout) link.

## Set Secrets

This value will contain the secrets (if your cloud function needs to). This value is optional so if you leave it in blank this configuration parameter won't be created in your cloud function properties.

When you need to configure a secret for a cloud function you must create the secret in GCP Secret Manager first. If you try to use a secret that doesn't exist in GCP, the cookiecutter will fail in the creation of the cloud function's source folder because it will search in GCP Secret Manager to create an environment variable in the .env file (for local testing).

You don't need to include the "snowflakeCredentials" here if you later configure the "snowflake_flag" to "Y".

## Set Environment Variables

This will set the environment variables your cloud function needs in the .env file. This value is optional so if you leave it in blank this configuration parameter won't be created in your cloud function properties.

## Trigger Bucket

This will set the trigger bucket if your cloud function needs to be triggered when an object is "finalized" in GCS. If you leave this in blank, no trigger bucket will be set.

## Snowflake Flag

This flag indicates if your cloud function needs to connect to Snowflake to perform SQL operations. The positive values for this flag are listed below:
- Y
- y
- Yes
- YES
- Yes

A different value will be taken as a negative for this flag.

When you set to "Y" the snowflake flag, a lot of (good) things will happen:
- The snowflake-connector will be included in your requirements.txt
- The runtime will be set to python 3.9 (the last version with Snowflake support)
- The vpc-connector will be set to use the VPC configured in GCP
- The egress-settings will be set to "all"
- New environment variables will be added to your .env file (including the secret credentials)
- New python functions will be added to your main.py file
