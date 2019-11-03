# modules.tf - Infrastructure as code generator - from visual diagrams to Terraform

[![Financial Contributors on Open Collective](https://opencollective.com/modulestf/all/badge.svg?label=financial+contributors)](https://opencollective.com/modulestf) [![MIT license](https://img.shields.io/github/license/antonbabenko/modules.tf-lambda.svg)]() [![Gitter](https://img.shields.io/gitter/room/modulestf/Lobby.svg)](https://gitter.im/modulestf/Lobby)


<a href="https://github.com/antonbabenko/modules.tf-lambda"><img src="https://raw.githubusercontent.com/antonbabenko/modules.tf-lambda/master/misc/modulestf-logo.png" alt="modules.tf - Infrastructure as code generator - from visual diagrams to Terraform" width="210" height="70" align="right" /></a>

This repository contains code for generating infrastructure as code from visual diagrams created in [Cloudcraft](https://cloudcraft.co).

Code in this repository has been already deployed to [AWS Lambda](https://aws.amazon.com/lambda/) and available for all [Cloudcraft](https://cloudcraft.co/app) users for free (forever):
* Draw your AWS architecture on [Cloudcraft](https://cloudcraft.co/app)
* Click "Export" and "Export as code (modules.tf)" at the top right side
* Download archive and unzip it
* Follow the instructions in `README.md` file to get resources created on your AWS account.

## Supporters

<a href="https://cloudcraft.co/" target="_blank"><img src="https://raw.githubusercontent.com/antonbabenko/modules.tf-lambda/master/misc/cloudcraft-logo.png" alt="Cloudcraft - the best way to draw AWS diagrams" width="211" height="56" align="right" /></a>

This project was partially sponsored by [Cloudcraft - the best way to draw AWS diagrams](https://cloudcraft.co).<br clear="all">

Monitoring of serverless applications provided by [Dashbird.io](https://dashbird.io/). <a href="https://dashbird.io/" target="_blank"><img src="https://raw.githubusercontent.com/antonbabenko/modules.tf-lambda/master/misc/dashbird-logo.png" alt="Dashbird - Monitor serverless applications" width="200" height="68" align="right" /></a><br clear="all">

## I am developer - show me the code & let's ship it!

Ok, if you are a developer and want to contribute, this is really great because [I](https://github.com/antonbabenko) need your help:

- Report, triage and fix bugs
- Refactor code
- Improve documentation
- Implement new sources and workflows (now only [Cloudcraft](https://cloudcraft.co/app) is partially supported)
- Consider contributing to [Terraform AWS modules](https://github.com/terraform-aws-modules) if you familiar with Terraform already

### Developer's guide

[AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html) supports Python 3.6, so you should use it also. Run this to install all required packages:

```
$ pip install -r requirements.txt
```

[Serverless framework](https://serverless.com) is used to do heavy-lifting by packaging dependencies required for AWS Lambda function (`requirements-lambda.txt`) and updating the code there. Read through [Quick Start guide](https://serverless.com/framework/docs/providers/aws/guide/quick-start/), as well as [installation](https://serverless.com/framework/docs/providers/aws/guide/installation/), [various AWS functions](https://serverless.com/framework/docs/providers/aws/guide/functions/), [serverless.yml reference](https://serverless.com/framework/docs/providers/aws/guide/serverless.yml/) to familiarise yourself with the usage of the framework.

As a short cheatsheet, you will need to use these commands:

* Invoke real endpoint in `dev` and `prod` environments using [httpie](https://github.com/jakubroztocil/httpie/):

```
# dev
$ http --print Hhb --all --follow https://dev-lambda.modules.tf/ @input/blueprint_my.json

# prod
$ http --print Hhb --all --follow https://lambda.modules.tf/ @input/blueprint_my.json
```

* Invoke function locally providing `input.json`:

```
$ serverless invoke local --function generate-cloudcraft --path test_fixtures/input_localfile.json
```

* Deploy all functions to `prod` environment:

```
$ serverless deploy --stage prod
```

* Deploy single function to `dev` environment:

```
$ serverless deploy function --function generate-cloudcraft --stage dev
```

* Deploy single function to `prod` environment:

```
$ serverless deploy function --function generate-cloudcraft --stage prod
```

## Known issues

* Serverless framework version shouldn't be newer than 1.51.0 unless [this](https://github.com/serverless/serverless/issues/6752) and [this](https://github.com/UnitedIncome/serverless-python-requirements/issues/414) bugs are fixed

## Authors

This project is created and maintained by [Anton Babenko](https://github.com/antonbabenko) with the help from [different contributors](https://github.com/antonbabenko/modules.tf-lambda/graphs/contributors).

[![@antonbabenko](https://img.shields.io/twitter/follow/antonbabenko.svg?style=social&label=Follow%20@antonbabenko%20on%20Twitter)](https://twitter.com/antonbabenko)


## Contributors

### Code Contributors

This project exists thanks to all the people who contribute. [[Contribute](CONTRIBUTING.md)].
<a href="https://github.com/antonbabenko/modules.tf-lambda/graphs/contributors"><img src="https://opencollective.com/modulestf/contributors.svg?width=890&button=false" /></a>

### Financial Contributors

Become a financial contributor and help us sustain our community. [[Contribute](https://opencollective.com/modulestf/contribute)]

#### Individuals

<a href="https://opencollective.com/modulestf"><img src="https://opencollective.com/modulestf/individuals.svg?width=890"></a>

#### Organizations

Support this project with your organization. Your logo will show up here with a link to your website. [[Contribute](https://opencollective.com/modulestf/contribute)]

<a href="https://opencollective.com/modulestf/organization/0/website"><img src="https://opencollective.com/modulestf/organization/0/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/1/website"><img src="https://opencollective.com/modulestf/organization/1/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/2/website"><img src="https://opencollective.com/modulestf/organization/2/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/3/website"><img src="https://opencollective.com/modulestf/organization/3/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/4/website"><img src="https://opencollective.com/modulestf/organization/4/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/5/website"><img src="https://opencollective.com/modulestf/organization/5/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/6/website"><img src="https://opencollective.com/modulestf/organization/6/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/7/website"><img src="https://opencollective.com/modulestf/organization/7/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/8/website"><img src="https://opencollective.com/modulestf/organization/8/avatar.svg"></a>
<a href="https://opencollective.com/modulestf/organization/9/website"><img src="https://opencollective.com/modulestf/organization/9/avatar.svg"></a>

## License

This work is licensed under MIT License. See LICENSE for full details.

Copyright (c) 2019 Anton Babenko
