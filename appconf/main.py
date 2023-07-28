"""
AWS AppConfig CLI
"""

import logging
import os
import sys

import boto3
import click
from rich.console import Console
from rich.logging import RichHandler
from rich.rule import Rule

from appconf import api
from appconf.exceptions import NoHostedConfigurationVersionsFound

logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])

console = Console()


@click.group()
@click.pass_context
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
def put_config(ctx, config_file, app, profile, description):
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


if __name__ == "__main__":
    cli(obj={})
