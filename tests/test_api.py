from unittest.mock import Mock, patch

from appconf.api import (
    get_application,
    get_config_profile,
    get_latest_hosted_configuration_version,
    get_deployment_strategy,
    get_environment,
    get_deployment,
    start_deployment,
    create_configuration,
    setup as api_setup,
)


def test_get_application(app_name, app_id, mock_api_list_applications):
    client = Mock()
    client.list_applications.return_value = mock_api_list_applications

    application = get_application(client, app_name)

    assert application.Name == app_name
    assert application.Id == app_id


def test_get_config_profile(
    app_id, config_profile_name, config_profile_id, mock_api_list_configuration_profiles
):
    client = Mock()
    client.list_configuration_profiles.return_value = (
        mock_api_list_configuration_profiles
    )

    config_profile = get_config_profile(client, app_id, config_profile_name)

    assert config_profile.ApplicationId == app_id
    assert config_profile.Name == config_profile_name
    assert config_profile.Id == config_profile_id


def test_get_latest_hosted_configuration_version(
    mock_api_list_hosted_configuration_versions, mock_application, mock_config_profile
):
    client = Mock()
    client.list_hosted_configuration_versions.return_value = (
        mock_api_list_hosted_configuration_versions
    )
    client.get_hosted_configuration_version.return_value = (
        mock_api_list_hosted_configuration_versions["Items"][0]
    )

    latest_hosted_config_profile = get_latest_hosted_configuration_version(
        client, mock_application, mock_config_profile
    )

    assert latest_hosted_config_profile.ApplicationId == mock_application.Id
    assert latest_hosted_config_profile.ConfigurationProfileId == mock_config_profile.Id
    assert latest_hosted_config_profile.VersionNumber == 1


def test_create_configuration(
    mock_application, mock_config_profile, mock_latest_config_profile
):
    client = Mock()
    client.create_hosted_configuration_version.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 201},
        "VersionNumber": 2,
    }

    with open("tests/fixtures/example.json", "r") as config_file:
        version = create_configuration(
            client,
            mock_application,
            mock_config_profile,
            config_file,
            "Example Configuration",
            latest_config_profile=mock_latest_config_profile,
        )

    assert version == 2


def test_get_deployment_strategy(
    mock_api_list_deployment_strategies, mock_deployment_strategy_id
):
    client = Mock()
    client.list_deployment_strategies.return_value = mock_api_list_deployment_strategies

    deployment_strategy = get_deployment_strategy(client, mock_deployment_strategy_id)

    assert deployment_strategy.Id == mock_deployment_strategy_id


def test_get_environment(mock_api_list_environments, mock_application):
    client = Mock()
    client.list_environments.return_value = mock_api_list_environments

    env_name = "default"

    env = get_environment(client, mock_application, env_name)

    assert env.Name == env_name
    assert env.State == "READY_FOR_DEPLOYMENT"


def test_start_deployment(
    mock_api_deployment,
    mock_application,
    mock_config_profile,
    mock_deployment_strategy,
    mock_environment,
):
    client = Mock()
    client.start_deployment.return_value = mock_api_deployment

    deployment = start_deployment(
        client,
        mock_application,
        mock_config_profile,
        mock_deployment_strategy,
        mock_environment,
    )

    assert deployment.ApplicationId == mock_application.Id
    assert deployment.EnvironmentId == mock_environment.Id
    assert deployment.DeploymentNumber == 1


def test_get_deployment(mock_api_deployment, mock_application, mock_environment):
    client = Mock()
    client.get_deployment.return_value = mock_api_deployment

    deployment = get_deployment(client, mock_application, mock_environment, 1)

    assert deployment.ApplicationId == mock_application.Id
    assert deployment.EnvironmentId == mock_environment.Id
    assert deployment.DeploymentNumber == 1


@patch("appconf.api.get_application")
@patch("appconf.api.get_config_profile")
def test_setup(
    mock_get_config_profile,
    mock_get_application,
    mock_application,
    mock_config_profile,
    app_name,
    config_profile_name,
):
    client = Mock()
    mock_get_config_profile.return_value = mock_config_profile
    mock_get_application.return_value = mock_application

    application, config_profile = api_setup(client, app_name, config_profile_name)

    assert application.Id == mock_application.Id
    assert config_profile.Id == mock_config_profile.Id
