# Application Insights

Summary describing the Bicep Application Insight Module.

App Insight Bicep Module with security requirements

## Parameters

Parameter name | Required | Description
-------------- | -------- | -----------
region         | Yes      | (Require) The Azure region into which the resources should be deployed.
tags           | Yes      | (Require) Resource Tags
appiName       | Yes      |
workspaceId    | Yes      | The ID of Log Analytics Workspace.
appiKind       | No       | (Optional) The kind of application that this component refers to, used to customize UI. This value is a freeform string, values should typically be one of the following: web, ios, other, store, java, phone.
appiAppType    | No       | (Optional)Type of application being monitored.
appiFlowType   | No       | (Optional) Used by the Application Insights system to determine what kind of flow this component was created by. This is to be set to Bluefield when creating/updating a component via the REST API.
appiInstKeyEnabled | No       | (Optional) Used by the Application Insights system with local authentication for use case not supported.

### region

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) The Azure region into which the resources should be deployed.

- Allowed values: `eastus`, `eastus2`, `westus`, `westus2`

### tags

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) Resource Tags

### appiName

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)



### workspaceId

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

The ID of Log Analytics Workspace.

### appiKind

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) The kind of application that this component refers to, used to customize UI. This value is a freeform string, values should typically be one of the following: web, ios, other, store, java, phone.

- Default value: `web`

- Allowed values: `web`, `ios`, `other`, `store`, `java`, `phone`

### appiAppType

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional)Type of application being monitored.

- Default value: `web`

- Allowed values: `web`, `other`

### appiFlowType

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Used by the Application Insights system to determine what kind of flow this component was created by. This is to be set to Bluefield when creating/updating a component via the REST API.

- Default value: `Bluefield`

### appiInstKeyEnabled

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Used by the Application Insights system with local authentication for use case not supported.

- Default value: `False`

## Outputs

Name | Type | Description
---- | ---- | -----------
appiId | string |
appiName | string |
appiIntConString | string |

## Snippets

### Parameter file

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "metadata": {
        "template": "modules/core/appinsights/main.json"
    },
    "parameters": {
        "region": {
            "value": ""
        },
        "tags": {
            "value": {}
        },
        "appiName": {
            "value": ""
        },
        "workspaceId": {
            "value": ""
        },
        "appiKind": {
            "value": "web"
        },
        "appiAppType": {
            "value": "web"
        },
        "appiFlowType": {
            "value": "Bluefield"
        },
        "appiInstKeyEnabled": {
            "value": false
        }
    }
}
```