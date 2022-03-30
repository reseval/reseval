# Reproducible Subjective Evaluation (ReSEval)
[![PyPI](https://img.shields.io/pypi/v/reseval.svg)](https://pypi.python.org/pypi/reseval)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Downloads](https://pepy.tech/badge/reseval)](https://pepy.tech/project/reseval)

ReSEval is a framework for quickly building subjective evaluations that are
deployed on crowdworker platforms like
[Amazon Mechanical Turk](https://www.mturk.com/). ReSEval currently supports
A/B, ABX, MOS, and MUSHRA tests on audio, image, text, and video data.

<h3 align="center">
    While our code is free to use, performing crowdsourced subjective
    evaluation is not free.<br/>We are not responsible for costs incurred
    while using our code.
</h3>


### Citation

If you use ReSEval in an academic publication, please cite
[our paper](https://www.maxrmorrison.com/pdfs/morrison2022reproducible.pdf).


### IEEE

M. Morrison, B. Tang, G. Tan, and B. Pardo, "Reproducible Subjective Evaluation," Submitted to ICLR 2022 Workshop on Setting up ML Evaluation Standards to Accelerate Progress, April 2022.


### BibTex

```
@inproceedings{morrison2022reproducible,
    title={Reproducible Subjective Evaluation},
    author={Morrison, Max and Tang, Brian and Tan, Gefei and Pardo, Bryan},
    booktitle={Submitted to ICLR 2022 Workshop on Setting up ML Evaluation Standards to Accelerate Progress},
    month={April},
    year={2022}
}
```


## Table of contents
- [Installation](#installation)
    * [Deploying locally](#deploying-locally)
- [Configuration](#configuration)
- [Adding files](#adding-files)
    * [AB](#ab)
    * [ABX](#abx)
    * [MOS](#mos)
    * [MUSHRA](#mushra)
- [Credentials](#credentials)
    * [Heroku](#heroku)
    * [Amazon Web Services](#amazon-web-services)
    * [Amazon Mechanical Turk](#amazon-mechanical-turk)
- [Usage](#usage)
    * [Command-line interface](#command-line-interface)
        * [Create](#create)
        * [Monitor](#monitor)
        * [Results](#results)
        * [Pay](#pay)
        * [Destroy](#destroy)
        * [Extend](#extend)
    * [Application programming interface](#application-programming-interface)
- [Advanced usage](#advanced-usage)
    * [CLI](#cli)
    * [API](#api)


## Installation

First, install the Python module. ReSEval requires Python 3.9 or higher.

`pip install reseval`

Next, [download Node.js](https://nodejs.org/en/). You can check that your installation is correct by running `node --version`. ReSEval uses Node.js version 17.4.0 and is not guaranteed to work on all versions. If needed, Linux and OS X users can use `n` to change their version of Node.js, and Windows users can use [NVM for Windows](https://github.com/coreybutler/nvm-windows).

```
# Linux or OS X
sudo npm install -g n
sudo n 17.4.0

# Windows
# Must be run with administrator privileges
nvm install 17.4.0
nvm use 17.4.0
```

**Note** - You must restart your terminal after changing versions of node for the change to take effect

### Deploying locally

To be able to preview your subjective evaluation locally, you must
[setup a local MySQL database](https://dev.mysql.com/doc/mysql-getting-started/en/)
and obtain a username and password. The default username is `root`.

Run the following to store the username and password in
`reseval.CACHE / '.env'`.

```
python -m reseval.credentials \
    --mysql_local_user <mysql_user> \
    --mysql_local_password <mysql_local_password>
```

The `.env` file is used to set local environment variables and is not pushed to
GitHub or uploaded to any remote storage.


## Configuration

All configuration is performed in a YAML configuration file. See `examples/*.yaml` for examples and documentation of parameters.


## Adding files

The files to be evaluated must be organized in a directory structure according
to the type of test being run. The directory structures for each test are as
follows. Examples of valid directories of evaluation files can be found in
`examples/`.


### AB

```
ab
├── <condition-1>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
└── <condition-2>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
```


### ABX

```
abx
└── reference
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
├── <condition-1>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
├── <condition-2>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
```


### MOS

```
mos
├── <condition-0>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
├── <condition-1>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
├── <condition-2>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
├── <condition-3>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
└── ...
```


### MUSHRA

```
mushra
├── <condition-0>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
├── <condition-1>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
├── <condition-2>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
├── <condition-3>
│   ├── <file-0>
│   ├── <file-1>
│   ├── <file-2>
│   ├── ...
└── ...
```


## Credentials

API keys are required to use the third-party services that ReSEval depends on.
These are not required for local development. Do not share these API keys.


### Heroku

Sign up for a Heroku account. Go to `Account Settings`. At the bottom of the page in the `API Key` section is a `Reveal` button.

<p align="center">
    <img src="docs/images/heroku-00.png" width="400" alt="Heroku API key instructions">
    <img src="docs/images/heroku-01.png" width="400" alt="Heroku API key instructions">
</p>

You will also need to enable billing. You can do so [here](https://heroku.com/verify).


### Amazon Web Services

Sign up for an AWS account. Go to `Security Credentials`. Under `Access keys`, click `Create New Access Key`.

<p align="center">
    <img src="docs/images/aws-00.png" width="400" alt="AWS API key instructions">
    <img src="docs/images/aws-01.png" width="400" alt="AWS API key instructions">
</p>


### Amazon Mechanical Turk

Follow the instructions [here](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkGettingStartedGuide/SetUp.html) for setting up MTurk and connecting it to your AWS account.


## Usage

Once you have your configuration file and a properly formatted directory of evaluation files, you are ready to deploy a subjective evaluation. Example configuration files and corresponding evaluation files can be found in `examples/`.

If you are not deploying locally, add your API keys.

```
python -m reseval.credentials \
    --aws_api_key <aws_api_key> \
    --aws_api_secret_key <aws_api_secret_key> \
    --heroku_api_key <heroku_api_key>
```

 API keys are saved in `reseval.CACHE / '.keys'`. The `.keys` file is used to set local environment variables and is not pushed to GitHub or uploaded to any remote storage.


### Command-line interface

 Arguments for the following command-line interfaces are as follows, unless otherwise specified.

- `<config>` - The configuration file
- `<directory>` - The directory of evaluation files
- `<name>` - The name of the evaluation given in the configuration file


#### Create

Create a subjective evaluation either locally, in remote development mode (e.g., MTurk Sandbox), or in production mode.

**Note** - `reseval.create` is not currently thread-safe. Wait until the first call has finished before calling it again. See [this GitHub issue](https://github.com/reseval/reseval/issues/5).

```
# Local development
python -m reseval.create <config> <directory> --local

# Remote development
python -m reseval.create <config> <directory>

# Production
python -m reseval.create <config> <directory> --production
```


#### Monitor

```
# Monitor all subjective evaluations
python -m reseval.monitor

# Monitor one subjective evaluation
# The name of the evaluation can be found in its configuration file
python -m reseval.monitor --name <name>
```

**Note** - By default, the monitor updates once every minute. You can update the monitor more or less often by providing an update interval in seconds.

```
# Update the monitor once every ten seconds
python -m reseval.monitor --interval 10
```


#### Results

```
# Get the results of a subjective evaluation.
# Results are stored in <directory>/<name>.
# <directory> defaults to the current directory.
python -m reseval.results <name> --directory <directory>
```


#### Pay

```
# Pay participants
python -m reseval.pay <name>
```


#### Destroy

```
# Destroy the compute resources of a subjective evaluation (e.g., any cloud
# storage, databases, or servers)
python -m reseval.destroy <name>

# Destroy a subjective evaluation even if it is still active.
# Participants who have taken the test so far will be paid.
python -m reseval.destroy <name> --force
```


#### Extend

```
# Add <participants> additional participants to a finished evaluation
python -m reseval.extend <name> <participants>
```


### Application programming interface

Documentation for our API can be found [here](https://reseval.github.io/reseval/html/index.html).


## Advanced usage

Once you feel comfortable with using ReSEval step-by-step from the
command-line and after you have added your credentials with
`reseval.credentials`, you can use the CLI or API to run your evaluation with
only a single command.


### CLI

```
# Local development
python -m reseval <config> <directory> --local

# Remote development
python -m reseval <config> <directory>

# Production
python -m reseval <config> <directory> --production
```


### API

```
import reseval

# Local development
reseval.run(config, directory, local=True)

# Remote development
reseval.run(config, directory)

# Production
reseval.run(config, directory, production=True)
```
