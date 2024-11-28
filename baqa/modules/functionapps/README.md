# Function App Module

Function App Module with service endpoint optional configuration, by default private.

Function App Bicep Module with security requirements

## Parameters

Parameter name | Required | Description
-------------- | -------- | -----------
region         | Yes      | (Require) The Azure region into which the resources should be deployed.
tags           | Yes      | (Require) Resource Tags
funcName       | Yes      | (Require) The application name. Nine (9) characters maximum
funcAspId      | Yes      | (Require) The app service plan id
funcAppiConnectionString | Yes      | (Require) Application insights InstrumentationKey
stName         | Yes      | (Require) The Name of Storage account.
funcVnetintId  | Yes      | (Optional) Vnet Int subnet ID
funcWorkerRuntimeString | No       | (Optional) The language worker runtime to load in the function app.
funcIdentityType | No       | (Optional) Type of managed service identity.
funcUserAssignedId | No       | (Optional) User manage identity ID
funcKind       | No       | (Optional) The name from Service Endpoint Subnet.
funcAppSettings | No       | (Optional) Application settings.
funcAlwayson   | No       | (Optional) Should the app be loaded at all times? Defaults to false.
funcFtpsState  | No       | (Optional) State of FTP / FTPS service
funcipSecurityRestrictionAction | No       | (Optional) Allow or Deny access for this IP range.
funcIpSecurityRestrictionName | No       | (Optional) 	IP restriction rule name.
funcIpSecurityRestrictionDescription | No       | (Optional) IP restriction rule description.
funcIpSecurityRestrictionHeader | No       | (Optional) IP restriction rule headers.
SubnetResourceIdsForServiceEndpoints | No       | (Optional) Virtual network subnet resource id
funcNetFrameworkVersion | No       | (Optional) The version of the .NET frameworks CLR used in this App Service. Possible values are v2.0 which will use the latest version of the .NET framework for the .NET CLR v2 - currently .net 3.5, v4.0 which corresponds to the latest version of the .NET CLR v4 - which at the time of writing is .net 4.7.1), v5.0 and v6.0.Defaults to v4.0.
funcUse32BitWorkerProcess | No       | true to use 32-bit worker process; otherwise, false.
funcConnectionStrings | No       | (Optional) Name of connection string, Connection value, and Type of database. For Example: ApiHub,Custom,DocDb,EventHub,MySql,NotificationHub,PostgreSQL,RedisCache,SQLAzure,SQLServer,ServiceBus. 
funcScmIpSecurityRestrictionsUseMain | No       | (Optional) IP security restrictions for scm to use main.
stIdentityType | No       | (Optional) Type of managed service identity.
stSku          | No       | (Optional) Gets or sets the SKU name. 
stkind         | No       | (Optional) Required. Indicates the type of storage account.
stAclBypass    | No       | (Optional) Specifies whether traffic is bypassed for Logging/Metrics/AzureServices. Possible values are any combination of Logging,Metrics,AzureServices (For example, "Logging, Metrics"), or None to bypass none of those traffics.
stAclDefaultAction | No       | (Optional) Specifies the default action of allow or deny when no other rules match.
stAclipRule    | No       | (Optional)Sets the IP ACL rules
stVirtualNetworkRules | No       | (Optional) Sets the virtual network rules

### region

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) The Azure region into which the resources should be deployed.

- Allowed values: `eastus`, `eastus2`, `westus`, `westus2`

### tags

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) Resource Tags

### funcName

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) The application name. Nine (9) characters maximum

### funcAspId

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) The app service plan id

### funcAppiConnectionString

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) Application insights InstrumentationKey

### stName

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Require) The Name of Storage account.

### funcVnetintId

![Parameter Setting](https://img.shields.io/badge/parameter-required-orange?style=flat-square)

(Optional) Vnet Int subnet ID

### funcWorkerRuntimeString

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) The language worker runtime to load in the function app.

- Default value: `dotnet`

### funcIdentityType

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Type of managed service identity.

- Default value: `SystemAssigned`

- Allowed values: `SystemAssigned`, `UserAssigned`, `SystemAssigned, UserAssigned`

### funcUserAssignedId

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) User manage identity ID

### funcKind

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) The name from Service Endpoint Subnet.

- Default value: `functionapp`

- Allowed values: `functionapp`, `functionapp,linux`, `functionapp,linux`, `container,kubernetes`, `functionapp,linux,kubernetes`

### funcAppSettings

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Application settings.

### funcAlwayson

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Should the app be loaded at all times? Defaults to false.

- Default value: `True`

### funcFtpsState

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) State of FTP / FTPS service

- Default value: `Disabled`

- Allowed values: `Disabled`, `FtpsOnly`

### funcipSecurityRestrictionAction

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Allow or Deny access for this IP range.

- Default value: `Allow`

### funcIpSecurityRestrictionName

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) 	IP restriction rule name.

- Default value: `IP Rule`

### funcIpSecurityRestrictionDescription

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) IP restriction rule description.

- Default value: `Allow access subnet service endpoints`

### funcIpSecurityRestrictionHeader

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) IP restriction rule headers.

### SubnetResourceIdsForServiceEndpoints

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Virtual network subnet resource id

### funcNetFrameworkVersion

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) The version of the .NET frameworks CLR used in this App Service. Possible values are v2.0 which will use the latest version of the .NET framework for the .NET CLR v2 - currently .net 3.5, v4.0 which corresponds to the latest version of the .NET CLR v4 - which at the time of writing is .net 4.7.1), v5.0 and v6.0.Defaults to v4.0.

- Default value: `v6.0`

### funcUse32BitWorkerProcess

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

true to use 32-bit worker process; otherwise, false.

- Default value: `False`

### funcConnectionStrings

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Name of connection string, Connection value, and Type of database. For Example: ApiHub,Custom,DocDb,EventHub,MySql,NotificationHub,PostgreSQL,RedisCache,SQLAzure,SQLServer,ServiceBus. 

### funcScmIpSecurityRestrictionsUseMain

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) IP security restrictions for scm to use main.

- Default value: `True`

### stIdentityType

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Type of managed service identity.

- Default value: `SystemAssigned`

### stSku

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Gets or sets the SKU name. 

- Default value: `Standard_LRS`

### stkind

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Required. Indicates the type of storage account.

- Default value: `StorageV2`

### stAclBypass

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Specifies whether traffic is bypassed for Logging/Metrics/AzureServices. Possible values are any combination of Logging,Metrics,AzureServices (For example, "Logging, Metrics"), or None to bypass none of those traffics.

- Default value: `None`

- Allowed values: `AzureServices`, `None`

### stAclDefaultAction

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Specifies the default action of allow or deny when no other rules match.

- Default value: `Deny`

- Allowed values: `Allow`, `Deny`

### stAclipRule

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional)Sets the IP ACL rules

### stVirtualNetworkRules

![Parameter Setting](https://img.shields.io/badge/parameter-optional-green?style=flat-square)

(Optional) Sets the virtual network rules

## Outputs

Name | Type | Description
---- | ---- | -----------
functionAppName | string |
functionId | string |
functionIdentityId | string |
functionStName | string |
functionStId | string |

## Snippets

### Parameter file

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "metadata": {
        "template": "modules/core/functionapp/main.json"
    },
    "parameters": {
        "region": {
            "value": ""
        },
        "tags": {
            "value": {}
        },
        "funcName": {
            "value": ""
        },
        "funcAspId": {
            "value": ""
        },
        "funcAppiConnectionString": {
            "value": ""
        },
        "stName": {
            "value": ""
        },
        "funcVnetintId": {
            "value": ""
        },
        "funcWorkerRuntimeString": {
            "value": "dotnet"
        },
        "funcIdentityType": {
            "value": "SystemAssigned"
        },
        "funcUserAssignedId": {
            "value": ""
        },
        "funcKind": {
            "value": "functionapp"
        },
        "funcAppSettings": {
            "value": {}
        },
        "funcAlwayson": {
            "value": true
        },
        "funcFtpsState": {
            "value": "Disabled"
        },
        "funcipSecurityRestrictionAction": {
            "value": "Allow"
        },
        "funcIpSecurityRestrictionName": {
            "value": "IP Rule"
        },
        "funcIpSecurityRestrictionDescription": {
            "value": "Allow access subnet service endpoints"
        },
        "funcIpSecurityRestrictionHeader": {
            "value": {}
        },
        "SubnetResourceIdsForServiceEndpoints": {
            "value": []
        },
        "funcNetFrameworkVersion": {
            "value": "v6.0"
        },
        "funcUse32BitWorkerProcess": {
            "value": false
        },
        "funcConnectionStrings": {
            "value": []
        },
        "funcScmIpSecurityRestrictionsUseMain": {
            "value": true
        },
        "stIdentityType": {
            "value": "SystemAssigned"
        },
        "stSku": {
            "value": "Standard_LRS"
        },
        "stkind": {
            "value": "StorageV2"
        },
        "stAclBypass": {
            "value": "None"
        },
        "stAclDefaultAction": {
            "value": "Deny"
        },
        "stAclipRule": {
            "value": []
        },
        "stVirtualNetworkRules": {
            "value": []
        }
    }
}
```