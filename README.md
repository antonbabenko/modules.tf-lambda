# modules.tf - Infrastructure as code generator - from visual diagrams to Terraform

[![MIT license](https://img.shields.io/github/license/antonbabenko/modules.tf-lambda.svg)]() [![Gitter](https://img.shields.io/gitter/room/modulestf/Lobby.svg)](https://gitter.im/modulestf/)


<a href="https://github.com/antonbabenko/modules.tf-lambda"><img src="https://raw.githubusercontent.com/antonbabenko/modules.tf-lambda/master/misc/modulestf-logo.png" alt="modules.tf - Infrastructure as code generator - from visual diagrams to Terraform" width="210" height="70" align="right" /></a>

This repository contains code for generating infrastructure as code from visual diagrams created in [Cloudcraft](https://cloudcraft.co).

Code in this repository has been already deployed to [AWS Lambda](https://aws.amazon.com/lambda/) and available for all [Cloudcraft](https://cloudcraft.co/app) users for free (forever):
* Draw your AWS architecture on [Cloudcraft](https://cloudcraft.co/app)
* Click "Export" and "Export as code (modules.tf)" at the top right side
* Download archive and unzip it
* Follow the instructions in `README.md` file to get resources created on your AWS account.

## Sponsors

<a href="https://cloudcraft.co/" target="_blank"><img src="https://raw.githubusercontent.com/antonbabenko/modules.tf-lambda/master/misc/cloudcraft-logo.png" alt="Cloudcraft - the best way to draw AWS diagrams" width="211" height="56" align="right" /></a>

This project was partially sponsored by [Cloudcraft - the best way to draw AWS diagrams](https://cloudcraft.co).

Don't hesitate to [contact me](mailto:anton@antonbabenko.com) if you want to become a sponsor or need custom features to be implemented.


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

## Authors

This project is created and maintained by [Anton Babenko](https://github.com/antonbabenko) with the help from [different contributors](https://github.com/antonbabenko/modules.tf-lambda/graphs/contributors).

[![@antonbabenko](https://img.shields.io/twitter/follow/antonbabenko.svg?style=social&label=Follow%20@antonbabenko%20on%20Twitter)](https://twitter.com/antonbabenko)


## License

This work is licensed under MIT License. See LICENSE for full details.

Copyright (c) 2018 Anton Babenko
