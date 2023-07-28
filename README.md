# AWS AppConfig CLI

**NOTE: This is still early in development**

> CLI tool for working with AWS AppConfig

This tool is designed to make working with [AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html) a little easier. The default API, and therefore the [AWS SDK's and CLI](https://docs.aws.amazon.com/cli/latest/reference/appconfig/index.html) tools rely on knowledge of obscure ID's to reference applications, profiles, environments etc. This CLI allows you to use the familiar names of these components as well as simplifying the interface to AppConfig.


### Current limitations
- Only supports Hosted Configuration AppConfig
- Only supports JSON formatted Hosted configuration
- Only supports getting & updating configuration


## Usage

```
> appconf --help
Usage: appconf [OPTIONS] COMMAND [ARGS]...

Options:
  --aws-profile TEXT  AWS Profile Name
  --help              Show this message and exit.

Commands:
  get  Get the current hosted configuration for the application & profile
  put  Upload a new hosted configuration version for the application &...
```

## Examples:

- Get current config: `appconf get --app <application name> --profile <profile name>`
- Put new config: 
  - `appconf put -a <application name> -p <profile name> path/to/config.json`
  - `appconf put -a <application name> -p <profile name> < cat path/to/config.json`
  - `cat path/to/config.json | appconf put -a <application name> -p <profile name>`
