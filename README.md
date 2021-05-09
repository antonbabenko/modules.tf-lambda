# Diagrams to code (d2c) - Infrastructure as code generator - from visual diagrams to Terraform

[![Financial Contributors on Open Collective](https://opencollective.com/modulestf/all/badge.svg?label=financial+contributors)](https://opencollective.com/modulestf) [![MIT license](https://img.shields.io/github/license/antonbabenko/modules.tf-lambda.svg)]() [![@antonbabenko](https://img.shields.io/twitter/follow/antonbabenko.svg?style=flat&label=Follow%20@antonbabenko%20on%20Twitter)](https://twitter.com/antonbabenko) 

<a href="https://github.com/antonbabenko/modules.tf-lambda"><img src="https://raw.githubusercontent.com/antonbabenko/modules.tf-lambda/master/misc/modulestf-logo.png" alt="modules.tf - Infrastructure as code generator - from visual diagrams to Terraform" width="210" height="70" align="right" /></a>

Code in this repository is used for generating infrastructure as Terraform configurations from visual diagrams created using [Cloudcraft](https://www.cloudcraft.co).


## How can I try this?

1. Sign up for a free account with [Cloudcraft](https://app.cloudcraft.co/signup).
1. Draw AWS architecture in web-browser (you can import live AWS resources, too).
1. Click "Export" and "Terraform code export" at the top right side.
1. Download archive and extract it locally.
1. Follow step-by-step instructions in `README.md` which you can find inside of it.


## How do the generated Terraform configurations look like?

In [modules.tf-demo](https://github.com/antonbabenko/modules.tf-demo) repository you can see the exact configuration code generated from sample "Web App Reference Architecture".

### Original infrastructure

<img src="https://raw.githubusercontent.com/antonbabenko/modules.tf-demo/master/Web%20App%20Reference%20Architecture%20(complete).png" alt="Web App Reference Architecture" width="500" />

### Recording of complete code execution

<a href="https://asciinema.org/a/32rkyxIBJ2K4taqZLSlKYNDDI" target="_blank"><img src="https://asciinema.org/a/32rkyxIBJ2K4taqZLSlKYNDDI.svg" alt="modules.tf demo - November 2019" width="500" /></a>

## Supporters

<a href="https://www.cloudcraft.co/" target="_blank"><img src="https://raw.githubusercontent.com/antonbabenko/modules.tf-lambda/master/misc/cloudcraft-logo.png" alt="Cloudcraft - the best way to draw AWS diagrams" width="211" height="56" align="right" /></a>

This project was partially sponsored by [Cloudcraft - the best way to draw AWS diagrams](https://www.cloudcraft.co).<br clear="all">

[Become a sponsor to @antonbabenko on GitHub](https://github.com/sponsors/antonbabenko/).

[![@antonbabenko](https://img.shields.io/twitter/follow/antonbabenko.svg?style=flat&label=Follow%20@antonbabenko%20on%20Twitter)](https://twitter.com/antonbabenko) 
[![@antonbabenko](https://img.shields.io/github/followers/antonbabenko?style=flat&label=Follow%20@antonbabenko%20on%20Github)](https://github.com/antonbabenko) 
[![modules.tf-lambda](https://img.shields.io/github/stars/antonbabenko/modules.tf-lambda?style=flat&label=Star%20modules.tf-lambda%20on%20Github)](https://github.com/antonbabenko/modules.tf-lambda)


## Developer's guide

This project is Python 3.8 serverless application written using [serverless.tf](https://serverless.tf) framework and open-source components ([Terraform AWS modules](https://github.com/terraform-aws-modules)).

### Notes for developers

Terraform is used to provision infrastructure resources as well as packaging artifacts and to do the deployments (check out [serverless.tf](https://serverless.tf) for more details).

Source code is located in `src/handler.py`.

Go to directory `terraform`, verify/update file `terraform.tfvars` and run:

```
$ terraform init     # Download required Terraform providers and modules
$ terraform apply    # Create or update infrastructure resources or do a new deployment of Lambda function (if source code has changed)
```

When infrastructure is created, you should be able to `POST` using [httpie](https://github.com/jakubroztocil/httpie/) or `curl` like this:

```
$ http --print Hhb --all --follow https://dev-d2c.modules.tf @test_fixtures/input/blueprint_my.json
```


## Contributors

### Code Contributors

This project exists thanks to all the people who contribute.
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

Copyright (c) 2018-2021 Anton Babenko
