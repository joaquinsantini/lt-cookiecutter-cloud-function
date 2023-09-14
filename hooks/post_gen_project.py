import os
import yaml
from typing import Any
from google.cloud import secretmanager


def access_secret_version(secret_id: str, version_id: str = "latest") -> str:
    """
    Function to access a secret in GCP

    Args:
        secret_id (str): A secret id (it must be created in GCP)
        version_id (str): The version of the secret. Default value is "latest"

    Returns:
        str: _description_
    """
    # Create the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version
    name = f"{secret_id}/versions/{version_id}"

    # Access the secret version
    response = client.access_secret_version(name=name)

    # Return the decoded payload
    return response.payload.data.decode("UTF-8")

def read_yaml_file(project_directory: str) -> Any:
    yaml_path = os.path.join(project_directory, "deploy.yaml")
    f = open(yaml_path)
    data = yaml.load(f, Loader=yaml.FullLoader)
    f.close()

    return data

def update_description(data: Any) -> Any:
    default_cloud_function_description = "Function purpose"
    cloud_function_description = "{{cookiecutter.cloud_function_description}}"

    if cloud_function_description == default_cloud_function_description:
        data["DEV"]["description"] = "{{cookiecutter.cloud_function_name}}"
    else:
        data["DEV"]["description"] = cloud_function_description

    return data

def update_memory(data: Any) -> Any:
    default_memory = "Memory in MB allowed. Left in blank for default (256Mb), e.g. 512, 1024"

    if "{{cookiecutter.memory}}" == default_memory:
        data["DEV"]["memory"] = 256
    else:
        data["DEV"]["memory"] = int("{{cookiecutter.memory}}")

    return data

def update_timeout(data: Any) -> Any:
    default_timeout = "Timeout in seconds. Left in blank for default (60s), e.g. 120, 360"

    if "{{cookiecutter.timeout}}" == default_timeout:
        data["DEV"]["timeout"] = 60
    else:
        data["DEV"]["timeout"] = int("{{cookiecutter.timeout}}")

    return data

def update_secrets(data: Any, project_directory: str) -> Any:
    env_file_path = os.path.join(project_directory, ".env")
    default_set_secrets = "Secrets exposed as environment variables. Left in blank if you don't need secrets, e.g. MY_CREDENTIALS=projects/de-cookiecutter-demo/secrets/myCredentials:latest"

    if "{{cookiecutter.set_secrets}}" != default_set_secrets:
        print("Reading secrets...")

        # Read secrets values from GCP
        l_secrets = "{{cookiecutter.set_secrets}}".split(",")
        dev_yaml_secrets = {}

        for secret in l_secrets:
            set_secrets_values = secret.split("=")
            secret_environment_variable = set_secrets_values[0]

            if set_secrets_values[1].find(":") >= 0:
                secret_id = set_secrets_values[1].split(":")[0]
                secret_version = set_secrets_values[1].split(":")[1]
            else:
                secret_id = "/".join(set_secrets_values[1].split("/")[0:4])
                secret_version = set_secrets_values[1].split("/")[5]

            secret_value = access_secret_version(
                secret_id=secret_id, version_id=secret_version
            )
            dev_yaml_secrets[secret_environment_variable] = set_secrets_values[1]

            # Update the .env file
            new_line = secret_environment_variable + "=" + secret_value + "\n"

            with open(env_file_path, "a") as f:
                f.write(new_line)

        # Update the deploy file
        data["DEV"]["secret-environment-variables"] = dev_yaml_secrets

    return data

def update_env_vars(data: Any, project_directory: str) -> Any:
    env_file_path = os.path.join(project_directory, ".env")
    default_set_env_vars = "Environment variables. Left in blank if you don't need environment variables, e.g. BUCKET=my-bucket-dev,OUTPUT_PATH=my_output_folder"

    if "{{cookiecutter.set_env_vars}}" != default_set_env_vars:
        print("Updating environment variables file...")

        # Read the environment variables
        env_vars = "{{cookiecutter.set_env_vars}}".split(",")
        yaml_env_vars = {}

        # Update the .env and deploy files
        for env_var in env_vars:
            env_var_name = env_var.split("=")[0].strip()
            env_var_value = env_var.split("=")[1].strip()
            yaml_env_vars[env_var_name] = env_var_value

            new_line = env_var.replace(" ", "").strip() + "\n"

            with open(env_file_path, "a") as f:
                f.write(new_line)

        data["DEV"]["environment-variables"] = yaml_env_vars

    return data

def update_trigger_bucket(data: Any) -> Any:
    trigger_bucket = "{{cookiecutter.trigger_bucket}}"
    default_trigger_bucket = "Trigger bucket. Left in blank if your cloud function trigger is HTTP"

    if trigger_bucket != default_trigger_bucket:
        print("Updating trigger bucket...")

        # Update deploy file
        data["DEV"]["trigger-bucket"] = trigger_bucket

    return data

def update_snowflake_related_items(data: Any, project_directory: str) -> Any:
    snowflake_flag = "{{cookiecutter.snowflake_flag}}"

    if snowflake_flag in ["Y", "y", "YES", "Yes", "yes"]:
        # Update requirements.txt
        requirements_path = os.path.join(project_directory, "requirements.txt")
        new_line = "snowflake-connector-python==3.1.0\n"

        with open(requirements_path, "a") as f:
            f.write(new_line)

        # Update deploy.yaml
        data["DEV"]["vpc-connector"] = "vpc-static-ip"
        data["DEV"]["egress-settings"] = "all"

        if "environment-variables" in data["DEV"]:
            data["DEV"]["environment-variables"]["SNOWFLAKE_WAREHOUSE"] = "DEV_WH"
            data["DEV"]["environment-variables"]["SNOWFLAKE_DATABASE"] = "DEV_DB"
        else:
            snowflake_vars = {
                "SNOWFLAKE_WAREHOUSE": "DEV_WH",
                "SNOWFLAKE_DATABASE": "DEV_DB",
            }
            data["DEV"]["environment-variables"] = snowflake_vars

        # Update snowflake secrets
        secret_id = "projects/679229687153/secrets/snowflakeCredentials"
        secret_yaml_value = (
            "projects/679229687153/secrets/snowflakeCredentials/versions/1"
        )
        secret_version = "1"
        secret_value = access_secret_version(
            secret_id=secret_id, version_id=secret_version
        )

        if "secret-environment-variables" in data["DEV"]:
            data["DEV"]["secret-environment-variables"][
                "SNOWFLAKE_CREDENTIALS"
            ] = secret_yaml_value
        else:
            data["DEV"]["secret-environment-variables"] = {
                "SNOWFLAKE_CREDENTIALS": secret_yaml_value
            }

        # Update snowflake environment variable
        env_file_path = os.path.join(project_directory, ".env")

        f = open(env_file_path, "r")
        env_source = f.read()
        f.close()

        if env_source.find("SNOWFLAKE_CREDENTIALS") < 0:
            new_line = "SNOWFLAKE_CREDENTIALS" + "=" + secret_value + "\n"

            with open(env_file_path, "a") as f:
                f.write(new_line)

        if env_source.find("SNOWFLAKE_WAREHOUSE") < 0:
            new_line = "SNOWFLAKE_WAREHOUSE" + "=" + "DEV_WH" + "\n"

            with open(env_file_path, "a") as f:
                f.write(new_line)

        if env_source.find("SNOWFLAKE_DATABASE") < 0:
            new_line = "SNOWFLAKE_DATABASE" + "=" + "DEV_DB" + "\n"

            with open(env_file_path, "a") as f:
                f.write(new_line)
    else:
        snowflake_utils_path = os.path.join(project_directory, "snowflake_utils.py")
        os.remove(snowflake_utils_path)

    return data

def main():
    print("Creating cloud source function folder...")

    # Set project directory
    project_directory = os.path.realpath(os.path.curdir)

    # Read deploy.yaml
    data = read_yaml_file(project_directory=project_directory)

    # Update cloud function description
    data = update_description(data=data)

    # Check default for memory
    data = update_memory(data=data)

    # Check default for timeout
    data = update_timeout(data=data)

    # Check default for set_secrets
    data = update_secrets(data=data, project_directory=project_directory)

    # Check default for set_env_vars
    data = update_env_vars(data=data, project_directory=project_directory)

    # Check default for trigger_bucket
    data = update_trigger_bucket(data=data)

    # Check default for snowflake_flag
    data = update_snowflake_related_items(data=data, project_directory=project_directory)

    # Save new version of deploy.yaml
    yaml_path = os.path.join(project_directory, "deploy.yaml")

    with open(yaml_path, "w") as f:
        yaml.dump(data, f, sort_keys=False)

    # Add config variable to deploy.yaml
    with open(yaml_path, "r") as f:
        config = f.read()

    config = config.replace("DEV:", "DEV: &config")

    with open(yaml_path, "w") as f:
        f.write(config)

    print("Cloud function source folder created!")


if __name__ == "__main__":
    main()
