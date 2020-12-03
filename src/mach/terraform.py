import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Union

import click
from mach import utils
from mach.templates import setup_jinja
from mach.types import MachConfig, Site


def generate_terraform(config: MachConfig):
    """Generate Terraform file from template and reformat it."""
    env = setup_jinja()
    template = env.get_template("site.tf")
    for site in config.sites:
        site_dir = config.deployment_path / Path(site.identifier)
        site_dir.mkdir(exist_ok=True)
        output_file = site_dir / Path("site.tf")
        content = _clean_tf(
            template.render(
                config=config, general_config=config.general_config, site=site
            )
        )
        with open(output_file, "w+") as fh:
            fh.write(content)
        click.echo(f"Generated file {output_file}")

        run_terraform("fmt", cwd=site_dir)


def _clean_tf(content: str) -> str:
    """Clean the Terraform file.

    The pyhcl (used in testing for example) doesn't like empty objects with newlines
    for example. Let's get rid of those.
    """
    return re.sub(r"\{(\s*)\}", "{}", content)


def plan_terraform(output_dir: Path):
    """Terraform init and plan for all generated sites."""
    for site_dir in output_dir.iterdir():
        if site_dir.is_dir():
            click.echo(f"Terraform plan for {site_dir.name}")
            run_terraform("init", site_dir)
            run_terraform("plan", site_dir)


def apply_terraform(
    config: MachConfig,
    *,
    with_sp_login: bool = False,
    auto_approve: bool = False,
    endpoint_redeploys: List[str] = [],
):
    """Terraform apply for all generated sites."""
    for site in config.sites:
        site_dir = config.deployment_path / Path(site.identifier)
        if not site_dir.is_dir():
            click.echo(f"Could not find site directory {site_dir}")
            continue

        click.echo(f"Applying Terraform for {site.identifier}")
        run_terraform("init", site_dir)

        if with_sp_login:
            azure_sp_login()

        for taint in _get_taints(site, endpoint_redeploys=endpoint_redeploys):
            click.echo(f"taint resource {taint}")
            run_terraform(["taint", taint], site_dir)

        cmd = ["apply"]
        if auto_approve:
            cmd += ["-auto-approve"]
        run_terraform(cmd, site_dir)


def azure_sp_login():
    """Login the service principal with az cli."""
    p = subprocess.run(
        [
            "az",
            "login",
            "--service-principal",
            "-u",
            os.environ["ARM_CLIENT_ID"],
            "-p",
            os.environ["ARM_CLIENT_SECRET"],
            "--tenant",
            os.environ["ARM_TENANT_ID"],
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    p.check_returncode()


def run_terraform(command: Union[List[str], str], cwd):
    """Run any Terraform command."""
    if isinstance(command, str):
        command = [command]
    p = subprocess.run(
        ["terraform", *command], cwd=cwd, stdout=sys.stdout, stderr=sys.stderr
    )
    p.check_returncode()


def _get_taints(site: Site, *, endpoint_redeploys: List[str]) -> List[str]:
    """Get resources that need to be tainted before an Terraform apply is executed.

    :param site: For which site to scan for resources that should be tainted
    :param endpoint_redeploys: List of endpoint keys of which the api gateway deployment should
        be redeployed
    """
    taints = []

    for endpoint in site.endpoints:
        if not endpoint.redeploy:
            continue
        slug = utils.slugify(endpoint.key)
        taints.append(f"aws_apigatewayv2_deployment.{slug}_default")

    for redeploy in endpoint_redeploys:
        slug = utils.slugify(redeploy)
        resource = f"aws_apigatewayv2_deployment.{slug}_default"
        if resource not in taints:
            taints.append(resource)

    return taints
