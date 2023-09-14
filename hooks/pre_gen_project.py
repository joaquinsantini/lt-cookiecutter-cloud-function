# Check an empty cloud function name
default_cloud_function_name = "A lowercase name, e.g. my-cloud-function"
cloud_function_name = "{{cookiecutter.cloud_function_name}}"

if cloud_function_name == default_cloud_function_name:
    raise Exception("The Cloud Function Name is mandatory!")
