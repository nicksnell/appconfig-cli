import logging

from appconf.models import Application, ConfigurationProfile, HostedConfigurationVersion
from appconf.exceptions import NoHostedConfigurationVersionsFound


def get_application(appconfig_client, app_name):
    """
    Get the application id from the application name
    """
    apps = appconfig_client.list_applications()

    for a in apps["Items"]:
        if a["Name"] == app_name:
            return Application.from_dict(a)

    return None


def get_config_profile(appconfig_client, app_id, profile_name):
    """
    Get the configuration profile from the application id and profile name
    """
    profiles = appconfig_client.list_configuration_profiles(ApplicationId=app_id)

    for p in profiles["Items"]:
        if p["Name"] == profile_name:
            return ConfigurationProfile.from_dict(p)

    return None


def get_latest_hosted_configuration_version(
    appconfig_client, application, config_profile
):
    """
    Get the latest hosted configuration version from the configuration profile id
    """
    config_versions = appconfig_client.list_hosted_configuration_versions(
        ApplicationId=application.Id, ConfigurationProfileId=config_profile.Id
    )

    if len(config_versions["Items"]) == 0:
        logging.error("No hosted configuration versions found!")
        raise NoHostedConfigurationVersionsFound(
            "No hosted configuration versions found!"
        )

    latest_version = config_versions["Items"][0]

    for v in config_versions["Items"]:
        if v["VersionNumber"] > latest_version["VersionNumber"]:
            latest_version = v

    latest_hosted_config = appconfig_client.get_hosted_configuration_version(
        ApplicationId=application.Id,
        ConfigurationProfileId=config_profile.Id,
        VersionNumber=latest_version["VersionNumber"],
    )

    return HostedConfigurationVersion.from_dict(latest_hosted_config)


def create_configuration(
    client,
    application,
    config_profile,
    config_file,
    description,
    latest_config_profile=None,
):
    """
    Create a new hosted configuration version for the application & profile
    """
    content = config_file.read().encode("utf-8")

    current_version = (
        latest_config_profile.VersionNumber if latest_config_profile else 0
    )

    try:
        response = client.create_hosted_configuration_version(
            ApplicationId=application.Id,
            ConfigurationProfileId=config_profile.Id,
            Description=description,
            Content=content,
            ContentType="application/json",
            LatestVersionNumber=current_version,
        )
    except Exception as e:
        logging.error(f"Error creating hosted configuration version: {e}")
        return

    if response["ResponseMetadata"]["HTTPStatusCode"] != 201:
        logging.error(f"Error creating hosted configuration version: {response}")
        return

    return response["VersionNumber"]


def setup(client, app_name, profile_name):
    application = get_application(client, app_name)

    if application is None:
        logging.error(f"Application {app_name} not found!")
        return

    config_profile = get_config_profile(client, application.Id, profile_name)

    if config_profile is None:
        logging.error(f"Configuration profile {profile_name} not found!")
        return

    return application, config_profile
