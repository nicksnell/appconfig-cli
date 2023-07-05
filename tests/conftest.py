import json
import pytest

from appconf.models import Application, ConfigurationProfile, HostedConfigurationVersion


@pytest.fixture
def app_name():
    return "app-name"


@pytest.fixture
def app_id():
    return "app-id"


@pytest.fixture
def config_profile_name():
    return "config-profile-name"


@pytest.fixture
def config_profile_id():
    return "config-profile-id"


@pytest.fixture
def mock_api_list_applications(app_name, app_id):
    return {
        "Items": [
            {
                "Id": app_id,
                "Name": app_name,
                "Description": "app-description",
                "Tags": {"app-tag-key": "app-tag-value"},
            }
        ]
    }


@pytest.fixture
def mock_api_list_configuration_profiles(
    app_id, config_profile_name, config_profile_id
):
    return {
        "Items": [
            {
                "ApplicationId": app_id,
                "Id": config_profile_id,
                "Name": config_profile_name,
                "Type": "AWS.Freeform",
            }
        ]
    }


@pytest.fixture
def mock_api_list_hosted_configuration_versions(app_id, config_profile_id):
    return {
        "Items": [
            {
                "ApplicationId": app_id,
                "ConfigurationProfileId": config_profile_id,
                "VersionNumber": 1,
                "Description": "config-description",
                "ContentType": "application/json",
                "Content": json.dumps({"key": "value"}),
            }
        ]
    }


@pytest.fixture
def mock_application(mock_api_list_applications):
    return Application.from_dict(mock_api_list_applications["Items"][0])


@pytest.fixture
def mock_config_profile(mock_api_list_configuration_profiles):
    return ConfigurationProfile.from_dict(
        mock_api_list_configuration_profiles["Items"][0]
    )


@pytest.fixture
def mock_latest_config_profile(mock_api_list_hosted_configuration_versions):
    return HostedConfigurationVersion.from_dict(
        mock_api_list_hosted_configuration_versions["Items"][0]
    )
