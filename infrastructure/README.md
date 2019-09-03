# AWS Greengrass Infrastructure #

Even though it's easy to setup things using the AWS Console (online AWS GUI),
this is not very good for documenting or reproducing it after.

This directory aims to contain infrastructure as code. It is not this project's
priority, therefore it may not be complete in its initial version, and may not
be compliant with best practices.

## Greengrass Subscriptions ##

- Stored in: `subscriptions.json`
- Help: `aws greengrass create-subscription-definition help`
- Deploy: `aws greengrass create-subscription-definition --initial-version <subscriptions.json content>`