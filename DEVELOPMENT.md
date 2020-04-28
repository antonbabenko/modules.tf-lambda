# Notes for developers

As a short cheatsheet, you will need to use these commands:

* Invoke real endpoint in `dev` and `prod` environments using [httpie](https://github.com/jakubroztocil/httpie/):

```
# dev
$ http --print Hhb --all --follow https://dev.modules.tf/ @input/blueprint_my.json

# prod
$ http --print Hhb --all --follow https://prod.modules.tf/ @input/blueprint_my.json
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

## Infrastructure

modules.tf can be self-hosted on your own infrastructure (if you want to expand it for some reason).

See [modules.tf-lambda-infra](https://github.com/antonbabenko/modules.tf-lambda-infra) repository for complete setup.

## Spellchecker

```
$ brew install codespell
$ pre-commit try-repo git://github.com/codespell-project/codespell codespell --all-files
```
