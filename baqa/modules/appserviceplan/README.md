# Application Plan

Summary describing the Bicep Application Plan Module

App Plan Bicep Module with security requirements

## Parameters

Parameter name | Required | Description
-------------- | -------- | -----------
region         | Yes      | (Require) The Azure region into which the resources should be deployed.
tags           | Yes      | (Require) Resource Tags
aspName        | Yes      | (Require) The app name for the AppService Plan.
aspSkuName     | No       | (Optional) Description of a SKU for a scalable resource.
aspKind        | No       | (Optional) Kind of resource.
aspSkuTier     | No       | (Optional) Service tier of the resource SKU.
aspSkuCapacity | No       | (Optional) Specifies the number of workers associated with this App Service Plan.
aspZoneRedundant | No       | (Optional) Specifies if the App Service Plan should be Zone Redundant.

### region

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) The Azure region into which the resources should be deployed.

- Allowed values: `eastus`, `eastus2`, `westus`, `westus2`

### tags

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) Resource Tags

### aspName

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) The app name for the AppService Plan.

### aspSkuName

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Description of a SKU for a scalable resource.

- Default value: `S1`

### aspKind

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Kind of resource.

- Default value: `windows`

- Allowed values: `linux`, `windows`, `app`, `elastic`, `xenon`, `functionapp`

### aspSkuTier

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Service tier of the resource SKU.

- Default value: `Standard`

- Allowed values: `Basic`, `Standard`, `PremiumV3`, `WorkflowStandard`

### aspSkuCapacity

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Specifies the number of workers associated with this App Service Plan.

- Default value: `1`

### aspZoneRedundant

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Specifies if the App Service Plan should be Zone Redundant.

- Default value: `False`

## Outputs

Name | Type | Description
---- | ---- | -----------
aspId | string | Output the farm id
aspName | string | Output the farm id

## Snippets

### Parameter file

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "metadata": {
        "template": "modules/core/appplan/main.json"
    },
    "parameters": {
        "region": {
            "value": ""
        },
        "tags": {
            "value": {}
        },
        "aspName": {
            "value": ""
        },
        "aspSkuName": {
            "value": "S1"
        },
        "aspKind": {
            "value": "windows"
        },
        "aspSkuTier": {
            "value": "Standard"
        },
        "aspSkuCapacity": {
            "value": 1
        },
        "aspZoneRedundant": {
            "value": false
        }
    }
}
```