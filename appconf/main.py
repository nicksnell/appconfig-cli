"""
AWS AppConfig CLI
"""

import logging
import os
import sys
import time

import boto3
import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress
from rich.rule import Rule

from appconf import api, __version__
from appconf.exceptions import NoHostedConfigurationVersionsFound

logging.basicConfig(level=logging.CRITICAL, handlers=[RichHandler()])

console = Console()


@click.group()
@click.pass_context
@click.version_option(__version__)
@click.option(
    "--aws-profile",
    help="AWS Profile Name",
    default=os.environ.get("AWS_DEFAULT_PROFILE_NAME", "default"),
)
def cli(ctx, aws_profile):
    ctx.ensure_object(dict)
    ctx.obj["session"] = boto3.session.Session(profile_name=aws_profile)
    ctx.obj["appconfig"] = ctx.obj["session"].client("appconfig")


@cli.command(name="get")
@click.pass_context
@click.option("-a", "--app", help="Application Name", required=True)
@click.option("-p", "--profile", help="Configuration profile name", required=True)
@click.option("-m", "--meta", help="Display metadata", default=False, is_flag=True)
def get_config(ctx, app, profile, meta):
    """
    Get the current hosted configuration for the application & profile
    """
    application, config_profile = api.setup(ctx.obj["appconfig"], app, profile)

    try:
        latest_hosted_config = api.get_latest_hosted_configuration_version(
            ctx.obj["appconfig"], application, config_profile
        )
    except NoHostedConfigurationVersionsFound:
        console.print(
            "[red]No hosted configuration versions found "
            f"for {application.Name} ({application.Id})![/red]"
        )
        return

    if meta:
        console.print(
            f"[blue bold]Application:[/blue bold] {application.Name} ({application.Id})"
        )
        console.print(
            f"[blue bold]Configuration:[/blue bold] {profile} ({config_profile.Id})"
        )
        console.print(
            f"[blue bold]Version:[/blue bold] {latest_hosted_config.VersionNumber}"
        )
        console.print(Rule())

    console.print_json(latest_hosted_config.get_json())


@cli.command(name="put")
@click.pass_context
@click.argument("config_file", type=click.File("r"), default=sys.stdin)
@click.option("-a", "--app", help="Application Name", required=True)
@click.option("-p", "--profile", help="Configuration profile name", required=True)
@click.option("-d", "--description", help="Description for the version", default="")
@click.option(
    "--deploy", is_flag=True, help="Deploy to configuration environment", default=False
)
@click.option(
    "--deploy-strategy",
    help="Deploy using named strategy",
    default="AppConfig.Linear50PercentEvery30Seconds",
)
@click.option("--env", help="Deploy to environment", default="default")
def put_config(
    ctx, config_file, app, profile, description, deploy, deploy_strategy, env
):
    """
    Upload a new hosted configuration version for the application & profile
    """
    application, config_profile = api.setup(ctx.obj["appconfig"], app, profile)

    try:
        latest_hosted_config = api.get_latest_hosted_configuration_version(
            ctx.obj["appconfig"], application, config_profile
        )
    except NoHostedConfigurationVersionsFound:
        latest_hosted_config = None

    version = api.create_configuration(
        ctx.obj["appconfig"],
        application,
        config_profile,
        config_file,
        description,
        latest_config_profile=latest_hosted_config,
    )

    console.print(f"[green]Created new configuration version:[/green] {version}")

    if deploy:
        strategy = api.get_deployment_strategy(ctx.obj["appconfig"], deploy_strategy)

        if strategy is None:
            console.print(
                f"[red]Unable to deploy configuration profile using strategy {strategy} "
                f"for {application.Name} ({application.Id})![/red]"
            )
            return

        environment = api.get_environment(ctx.obj["appconfig"], application, env)

        deployment = api.start_deployment(
            ctx.obj["appconfig"], application, config_profile, strategy, environment
        )

        with Progress() as progress:
            task = progress.add_task("Deployment in progress...", total=100)
            complete_so_far = 0

            while deployment.PercentageComplete != 100.0:
                time.sleep(20)
                deployment = api.get_deployment(
                    ctx.obj["appconfig"],
                    application,
                    environment,
                    deployment.DeploymentNumber,
                )
                percent_complete = int(deployment.PercentageComplete)
                advance = percent_complete - complete_so_far
                progress.update(task, advance=advance)
                complete_so_far = percent_complete

            progress.update(task, visible=False)

        console.print(
            f"[green]Successful deployment to [/green] {env} [green](took "
            f"{deployment.FinalBakeTimeInMinutes} minute"
            f"{'s' if deployment.FinalBakeTimeInMinutes > 1 else ''})[/green]"
        )


if __name__ == "__main__":
    cli(obj={})
