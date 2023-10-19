# The code in this repository has been migrated to the [Nautobot SSoT Repository](https://github.com/nautobot/nautobot-plugin-ssot) as an integration - read more about it in the [SSoT Docs](https://docs.nautobot.com/projects/ssot/en/latest/admin/install/)! As of August 2023 this repository has been **FROZEN** - all development / issues / discussions for this integration are in the [Nautobot SSoT Repository](https://github.com/nautobot/nautobot-plugin-ssot) going forward.

# Nautobot SSoT Infoblox

Using the [Nautobot SSoT](https://github.com/nautobot/nautobot-plugin-ssot) framework, the SSoT plugin for Infoblox allows for synchronizing of IP network and VLAN data between [Infoblox](https://infoblox.com/) and [Nautobot](https://github.com/nautobot/nautobot).

## Installation

The plugin is available as a Python package in PyPi and can be installed with pip.

```shell
pip install nautobot-ssot-infoblox
```

> The plugin is compatible with Nautobot 1.2.0 and higher

To ensure Nautobot SSoT Infoblox is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-ssot-infoblox` package:

```no-highlight
# echo nautobot-ssot-infoblox >> local_requirements.txt
```

Once installed, the plugin needs to be enabled in your `nautobot_config.py`

```python
# In your nautobot_config.py
PLUGINS = ["nautobot_ssot", "nautobot_ssot_infoblox"]
```

See the section below for configuration settings.

## Configuration

| Setting                           | Default | Description                                                            |
| --------------------------------- | ------- | ---------------------------------------------------------------------- |
| NAUTOBOT_INFOBLOX_URL             | N/A     | URL of the Infoblox instance to sync with.                             |
| NAUTOBOT_INFOBLOX_USERNAME        | N/A     | The username to authenticate against Infoblox with.                    |
| NAUTOBOT_INFOBLOX_PASSWORD        | N/A     | The password to authenticate against Infblox with.                     |
| NAUTOBOT_INFOBLOX_VERIFY_SSL      | True    | Toggle SSL verification when syncing data with Infoblox.               |
| NAUTOBOT_INFOBLOX_WAPI_VERSION    | v2.12   | The version of the Infoblox API.                                       |
| enable_sync_to_infoblox           | False   | Add job to sync data from Nautobot into Infoblox.                      |
| enable_rfc1918_network_containers | False   | Add job to sync network containers to Nautobot (top level aggregates). |
| default_status                    | active  | Default Status to be assigned to imported objects.                     |
| infoblox_import_objects           | True    | Dictionary with keys for each import object and the value define import.|
| infoblox_import_subnets           | N/A     | List of Subnets in CIDR string notation to filter import to.           |

### Configuration Example

```python
PLUGINS_CONFIG = {
    "nautobot_ssot": {
        "hide_example_jobs": True,  # defaults to False if unspecified
    }
    "nautobot_ssot_infoblox": {
        "NAUTOBOT_INFOBLOX_URL": os.getenv("NAUTOBOT_INFOBLOX_URL", ""),
        "NAUTOBOT_INFOBLOX_USERNAME": os.getenv("NAUTOBOT_INFOBLOX_USERNAME", ""),
        "NAUTOBOT_INFOBLOX_PASSWORD": os.getenv("NAUTOBOT_INFOBLOX_PASSWORD", ""),
        "NAUTOBOT_INFOBLOX_VERIFY_SSL": os.getenv("NAUTOBOT_INFOBLOX_VERIFY_SSL", "true"),
        "NAUTOBOT_INFOBLOX_WAPI_VERSION": os.getenv("NAUTOBOT_INFOBLOX_WAPI_VERSION", "v2.12"),
        "enable_sync_to_infoblox": False,
        "enable_rfc1918_network_containers": False,
        "default_status": "active",
        "infoblox_import_objects": {
            "vlan_views": os.getenv("NAUTOBOT_INFOBLOX_IMPORT_VLAN_VIEWS", True),
            "vlans": os.getenv("NAUTOBOT_INFOBLOX_IMPORT_VLANS", True),
            "subnets": os.getenv("NAUTOBOT_INFOBLOX_INFOBLOX_IMPORT_SUBNETS", True),
            "ip_addresses": os.getenv("NAUTOBOT_INFOBLOX_IMPORT_IP_ADDRESSES", True),
        },
        "infoblox_import_subnets": ["10.46.128.0/18", "192.168.1.0/24"],
    }
}
```

## DiffSync Models

Below are the data mappings between objects within Infoblox and the corresponding objects within Nautobot:

| Infoblox          | Nautobot       |
| ----------------- | -------------- |
| Network           | Prefix         |
| IP Address        | IP Address     |
| VLAN              | VLAN           |
| VLAN view         | VLAN Group     |
| Network container | Aggregate      |
| Extensibility Attrs | Custom Fields |

NOTE - More information about Extensibility Attributes can be found in the [project documentation](#project-documentation).

### DiffSyncModel - Network

![Diffsync Model - Network](./docs/static/diffsyncmodel-network.png)

### DiffSyncModel - IPAddress

![Diffsync Model - IPAddress](./docs/static/diffsyncmodel-ipaddress.png)

### DiffSyncModel - Aggregate

![Diffsync Model - Aggregate](./docs/static/diffsyncmodel-aggregate.png)

## Contributing

Pull requests are welcomed and automatically built and tested against multiple version of Python and multiple version of Nautobot through GitHub Actions.

The project is packaged with a light development environment based on `docker-compose` to help with the local development of the project and to run the tests within GitHub Actions.

The project is following Network to Code software development guideline and is leveraging:

- Black, Pylint, Bandit and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

### Development Environment

The development environment can be used in 2 ways. First, with a local poetry environment if you wish to develop outside of Docker with the caveat of using external services provided by Docker for PostgresQL and Redis. Second, all services are spun up using Docker and a local mount so you can develop locally, but Nautobot is spun up within the Docker container.

Below is a quick start guide if you're already familiar with the development environment provided, but if you're not familiar, please read the [Getting Started Guide](GETTING_STARTED.md).

#### Invoke

The [PyInvoke](http://www.pyinvoke.org/) library is used to provide some helper commands based on the environment.  There are a few configuration parameters which can be passed to PyInvoke to override the default configuration:

- `nautobot_ver`: the version of Nautobot to use as a base for any built docker containers (default: 1.1.4)
- `project_name`: the default docker compose project name (default: nautobot_ssot_infoblox)
- `python_ver`: the version of Python to use as a base for any built docker containers (default: 3.6)
- `local`: a boolean flag indicating if invoke tasks should be run on the host or inside the docker containers (default: False, commands will be run in docker containers)
- `compose_dir`: the full path to a directory containing the project compose files
- `compose_files`: a list of compose files applied in order (see [Multiple Compose files](https://docs.docker.com/compose/extends/#multiple-compose-files) for more information)

Using **PyInvoke** these configuration options can be overridden using [several methods](http://docs.pyinvoke.org/en/stable/concepts/configuration.html).  Perhaps the simplest is simply setting an environment variable `INVOKE_NAUTOBOT_SSOT_INFOBLOX_VARIABLE_NAME` where `VARIABLE_NAME` is the variable you are trying to override.  The only exception is `compose_files`, because it is a list it must be overridden in a yaml file.  There is an example `invoke.yml` (`invoke.example.yml`) in this directory which can be used as a starting point.

#### Local Poetry Development Environment

1. Copy `development/creds.example.env` to `development/creds.env` (This file will be ignored by Git and Docker)
2. Uncomment the `POSTGRES_HOST`, `REDIS_HOST`, and `NAUTOBOT_ROOT` variables in `development/creds.env`
3. Create an `invoke.yml` file with the following contents at the root of the repo (you can also `cp invoke.example.yml invoke.yml` and edit as necessary):

```yaml
---
nautobot_ssot_infoblox:
  local: true
  compose_files:
    - "docker-compose.requirements.yml"
```

3. Run the following commands:

```shell
poetry shell
poetry install --extras nautobot
export $(cat development/dev.env | xargs)
export $(cat development/creds.env | xargs) 
invoke start && sleep 5
nautobot-server migrate
```

> If you want to develop on the latest develop branch of Nautobot, run the following command: `poetry add --optional git+https://github.com/nautobot/nautobot@develop`. After the `@` symbol must match either a branch or a tag.

4. You can now run nautobot-server commands as you would from the [Nautobot documentation](https://nautobot.readthedocs.io/en/latest/) for example to start the development server:

```shell
nautobot-server runserver 0.0.0.0:8080 --insecure
```

Nautobot server can now be accessed at [http://localhost:8080](http://localhost:8080).

It is typically recommended to launch the Nautobot **runserver** command in a separate shell so you can keep developing and manage the webserver separately.

#### Docker Development Environment

This project is managed by [Python Poetry](https://python-poetry.org/) and has a few requirements to setup your development environment:

1. Install Poetry, see the [Poetry Documentation](https://python-poetry.org/docs/#installation) for your operating system.
2. Install Docker, see the [Docker documentation](https://docs.docker.com/get-docker/) for your operating system.

Once you have Poetry and Docker installed you can run the following commands to install all other development dependencies in an isolated python virtual environment:

```shell
poetry shell
poetry install
invoke start
```

Nautobot server can now be accessed at [http://localhost:8080](http://localhost:8080).

To either stop or destroy the development environment use the following options.

- **invoke stop** - Stop the containers, but keep all underlying systems intact
- **invoke destroy** - Stop and remove all containers, volumes, etc. (This results in data loss due to the volume being deleted)

### CLI Helper Commands

The project is coming with a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. The commands are listed below in 3 categories `dev environment`, `utility` and `testing`.

Each command can be executed with `invoke <command>`. Environment variables `INVOKE_NAUTOBOT_SSOT_INFOBLOX_PYTHON_VER` and `INVOKE_NAUTOBOT_SSOT_INFOBLOX_NAUTOBOT_VER` may be specified to override the default versions. Each command also has its own help `invoke <command> --help`

#### Docker dev environment

```no-highlight
  build            Build all docker images.
  debug            Start Nautobot and its dependencies in debug mode.
  destroy          Destroy all containers and volumes.
  restart          Restart Nautobot and its dependencies.
  start            Start Nautobot and its dependencies in detached mode.
  stop             Stop Nautobot and its dependencies.
```

#### Utility

```no-highlight
  cli              Launch a bash shell inside the running Nautobot container.
  create-user      Create a new user in django (default: admin), will prompt for password.
  makemigrations   Run Make Migration in Django.
  nbshell          Launch a nbshell session.
  shell-plus       Launch a shell_plus session, which uses iPython and automatically imports all models.
```

#### Testing

```no-highlight
  bandit           Run bandit to validate basic static code security analysis.
  black            Run black to check that Python files adhere to its style standards.
  flake8           This will run flake8 for the specified name and Python version.
  pydocstyle       Run pydocstyle to validate docstring formatting adheres to NTC defined standards.
  pylint           Run pylint code analysis.
  tests            Run all tests for this plugin.
  unittest         Run Django unit tests for the plugin.
```

### Project Documentation

Project documentation is generated by [mkdocs](https://www.mkdocs.org/) from the documentation located in the docs folder.  You can configure [readthedocs.io](https://readthedocs.io/) to point at this folder in your repo.  A container hosting the docs will be started using the invoke commands on [http://localhost:8001](http://localhost:8001), as changes are saved the docs will be automatically reloaded.

## Questions

For any questions or comments, please check the [FAQ](FAQ.md) first and feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #networktocode).
Sign up [here](http://slack.networktocode.com/)

## Screenshots

![Infoblox SSoT Status](./docs/static/ssot-status.png)

![Infoblox SSoT Logs](./docs/static/ssot-logs.png)
