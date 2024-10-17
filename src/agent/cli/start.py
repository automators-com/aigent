import os
import typer
import tomllib
from pathlib import Path
from typing_extensions import Annotated
from rich.console import Console
from agent.completions import agent
from agent.logging import logger
from agent.config import TEST_DIR, read_config

err_console = Console(stderr=True)


def start(
    prompt: Annotated[
        str, typer.Option(help="A prompt describing the scope of your tests.")
    ],
    url: Annotated[
        str,
        typer.Option(help="A url that acts as an entrypoint to app you're testing."),
    ],
    clean: Annotated[
        bool,
        typer.Option(
            help="Delete files from the 'tests' directory before starting the agent."
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(help="Enable debug mode for additional logs and file writing."),
    ] = False,
    headless: Annotated[
        bool,
        typer.Option(help="Run the browser in headless mode."),
    ] = False,
    language: Annotated[
        str,
        typer.Option(help="The programming language to generate tests in."),
    ] = "python",
    framework: Annotated[
        str,
        typer.Option(help="The framework to use for testing."),
    ] = "playwright",
):
    """Starts the test generation agent ✨"""

    config = read_config()

    # CLI args should take precedence over config file
    if prompt is not None:
        config["agent"]["prompt"] = prompt
    if url is not None:
        config["agent"]["url"] = url
    if headless:
        config["config"]["headless"] = headless
    if debug:
        config["config"]["log_level"] = "DEBUG"
    if clean:
        config["config"]["clean"] = clean
    if language:
        config["agent"]["language"] = language
    if framework:
        config["agent"]["framework"] = framework

    # perform actions based on config
    if str(config["config"]["log_level"]).lower() == "debug":
        logger.setLevel("DEBUG")
        os.environ["LOG_LEVEL"] = "DEBUG"

    if str(config["config"]["headless"]).lower() == "true":
        os.environ["HEADLESS"] = "true"

    if str(config["config"]["clean"]).lower() == "true":
        logger.info(f"Deleting files in the {TEST_DIR} directory")
        os.popen(f"rm -rf {TEST_DIR}/*").read()

    # raise an error if required config is missing
    for item in ["url", "prompt"]:
        if config["agent"].get(item) is None:
            err_console.print(
                f"Please set agent.{item} in the config.toml file or pass it as the --{item} CLI option."
            )
            raise typer.Exit()

    # call the agent
    agent(
        prompt=config["agent"]["prompt"],
        url=config["agent"]["url"],
    )
