import typer
import subprocess
from pathlib import Path
import shutil
from agent.logging import logger


def delete_entire_dir(dir: Path | str) -> None:
    """Delete all files and folders in a directory

    :param dir: The directory to delete
    :type dir: Path | str
    """
    shutil.rmtree(Path(dir), ignore_errors=True)


def check_for_node():
    """Checks if node.js in installed on the system"""
    try:
        logger.info("Checking that Node.js is installed.")
        version = subprocess.check_output(["node", "-v"])
        if version:
            logger.info(f"found node version: {version.decode().strip()}")

        return version.decode().strip()
    except Exception as e:
        logger.error(
            f"Could not find Node.js installation. Please install it from https://nodejs.org : {e}"
        )
        raise typer.Exit()


def check_for_npm():
    """Checks if npm is installed on the system"""
    try:
        logger.info("Checking that npm is installed.")
        version = subprocess.check_output(["npm", "-v"])
        if version:
            logger.info(f"found npm version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def check_for_playwright():
    """Checks if playwright is installed on the system"""
    try:
        logger.info("Checking that Playwright is installed.")
        version = subprocess.check_output(["playwright", "--version"])
        if version:
            logger.info(f"found playwright version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def check_for_cypress():
    """Checks if cypress is installed on the system"""
    try:
        logger.info("Checking that Cypress is installed.")
        version = subprocess.check_output(["cypress", "--version"])
        if version:
            logger.info(f"found cypress version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def scaffold_playwright(
    test_dir: Path | str,
    language: str,
    clean=True,
) -> None:
    """Scaffolds a playwright test environment

    :param test_dir: Path to the test directory
    :type test_dir: Path
    :param language: The language to scaffold the test environment in (python, typescript or javascript)
    :type language: str
    :param clean: Whether to clean out the test directory before scaffolding, defaults to True
    :type clean: bool, optional
    """
    # ensure test_dir is a Path object
    test_dir = Path(test_dir)

    # clean out the test directory
    if clean:
        delete_entire_dir(test_dir)

    # create the test directory
    test_dir.mkdir(exist_ok=True)

    # nothing to do for python
    if language == "python":
        return None

    # run the playwright init command
    logger.info("Running the playwright install command.")
    lang = "Typescript" if language == "typescript" else "js"
    cmd = [
        "npm",
        "init",
        "playwright",
        "--",
        "--yes",
        "--quiet",
        "--install-deps",
        "--no-examples",
        "--browser=chromium",
        f"--lang={lang}",
        ".",  # scaffold in the test_dir based on cwd set below
    ]
    print(cmd)
    subprocess.run(
        cmd,
        cwd=test_dir,
    )

    logger.info("Adding dev dependencies.")
    subprocess.run(
        ["npm", "install", "uuid", "--save-dev"],
        cwd=test_dir,
    )


def check_for_playwright_browsers(
    test_dir: Path,
):
    """Checks if playwright browsers are installed on the system"""
    try:
        logger.info("Checking that Playwright browsers are installed.")
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            cwd=test_dir,
        )
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False
    return True


def check_for_cypress_installation(test_dir: Path):
    """Checks if cypress is installed on the system"""
    try:
        logger.info("Checking that Cypress is installed.")
        subprocess.run(
            ["npx", "--yes", "cypress", "install"],
            check=True,
            cwd=test_dir,
        )
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def scaffold_cypress(test_dir: Path, language: str, clean=True) -> None:
    """Scaffolds a playwright test environment

    :param test_dir: Path to the test directory
    :type test_dir: Path
    :param language: The language to scaffold the test environment in (python, typescript or javascript)
    :type language: str
    :param clean: Whether to clean out the test directory before scaffolding, defaults to True
    :type clean: bool, optional
    """

    # ensure test_dir is a Path object
    test_dir = Path(test_dir)

    # clean out the test directory
    if clean:
        delete_entire_dir(test_dir)

    # create the test directory
    test_dir.mkdir(exist_ok=True)

    # nothing to do for python
    if language == "python":
        return None

    # run the playwright init command
    logger.info("Setting up cypress environment.")
    # create a package.json file
    with open(test_dir / "package.json", "w") as f:
        f.write(
            """{
  "name": "agent-tests",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "cypress": "latest",
    "uuid": "latest",
    "typescript": "latest"
  }
}
            """
        )

    # add a gitignore file
    logger.info("Adding a .gitignore file.")
    with open(test_dir / ".gitignore", "w") as f:
        f.write(
            """
node_modules/
.cypress/
            """
        )

    if language == "typescript":
        logger.info("Adding a cypress.config.ts file.")
        with open(test_dir / "cypress.config.ts", "w") as f:
            f.write(
                """import { defineConfig } from 'cypress'

export default defineConfig({
  defaultCommandTimeout: 10000,
  e2e: {
  
  },
})
"""
            )

        logger.info("Adding a tsconfig.json file.")
        with open(test_dir / "tsconfig.json", "w") as f:
            f.write(
                """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["es5", "dom"],
    "types": ["cypress", "node"]
  },
  "include": ["**/*.ts"]
}
"""
            )

    if language == "javascript":
        logger.info("Adding a cypress.config.js file.")
        with open(test_dir / "cypress.config.js", "w") as f:
            f.write(
                """const { defineConfig } = require('cypress')

module.exports = defineConfig({
  defaultCommandTimeout: 10000,
})
"""
            )

    logger.info("Installing npm dependencies.")
    subprocess.run(
        ["npm", "install"],
        cwd=test_dir,
    )
