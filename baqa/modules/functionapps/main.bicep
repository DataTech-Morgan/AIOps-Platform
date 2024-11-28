// Common Parameters
//*****************************************************************************************************
@description('(Require) The Azure region into which the resources should be deployed.')
@allowed([
  'eastus'
  'eastus2'
  'westus'
  'westus2'
])
param region string

@description('(Require) Resource Tags')
param tags object
//*****************************************************************************************************


// Require Parameters Function App 
//*****************************************************************************************************
@description('(Require) The application name. Nine (9) characters maximum')
@maxLength(60)
param funcName string

@description('(Require) The app service plan id')
param funcAspId string 

@description('(Require) Application insights InstrumentationKey')
param funcAppiConnectionString string

@description('(Require) The Name of Storage account.')
@maxLength(24)
param stName string

@description('(Optional) Vnet Int subnet ID')
param funcVnetintId  string

// @description('(Optional) Github Runner Dev Subnet ID')
// param githubSubnetDevIpAdress  string

// @description('(Optional) Github Runner Prod Subnet ID')
// param githubSubnetProdIpAdress  string
//*****************************************************************************************************


// Function App Optional Parameters
//*****************************************************************************************************
@description('(Optional) The language worker runtime to load in the function app.')
param funcWorkerRuntimeString string

@description('(Optional) Type of managed service identity.')
@allowed([ 'SystemAssigned', 'UserAssigned', 'SystemAssigned, UserAssigned' ])
param funcIdentityType string = 'SystemAssigned'

@description('(Optional) User manage identity ID')
param funcUserAssignedId string = ''

@description('(Optional) The name from Service Endpoint Subnet.')
@allowed([ 
  'functionapp'
  'functionapp,linux'
  'container,kubernetes'
  'functionapp,linux,kubernetes'
])
param funcKind string = 'functionapp,linux'

// @description('(Optional) Application settings.')
// param funcAppSettings object = {}

@description('(Optional) Should the app be loaded at all times? Defaults to false.')
param funcAlwayson bool = true

@description('(Optional) State of FTP / FTPS service')
@allowed([
 'Disabled'
 'FtpsOnly'
])
param funcFtpsState string = 'FtpsOnly'

@description('(Optional) Allow or Deny access for this IP range.')
param funcipSecurityRestrictionAction string = 'Allow'

@description('(Optional) 	IP restriction rule name.')
param funcIpSecurityRestrictionName string = 'IP Rule'

@description('(Optional) IP restriction rule description.')
param funcIpSecurityRestrictionDescription string = 'Allow access subnet service endpoints'

//@description('(Optional) IP restriction rule headers.')
//param funcIpSecurityRestrictionHeader object = {}

@description('(Optional) Virtual network subnet resource id')
param SubnetResourceIdsForServiceEndpoints string = ''

param githubsunetdevId string =  '/subscriptions/d4d0f058-7e80-4f34-a150-61cedb5629ed/resourceGroups/rg-mw-prod-hubvnet-eastus2-a/providers/Microsoft.Network/virtualNetworks/vnet-mw-prod-hub-eastus2-a/subnets/snet-mw-dev-githubrunners-eastus2-a'
param githubsunetprodId string = '/subscriptions/d4d0f058-7e80-4f34-a150-61cedb5629ed/resourceGroups/rg-mw-prod-hubvnet-eastus2-a/providers/Microsoft.Network/virtualNetworks/vnet-mw-prod-hub-eastus2-a/subnets/snet-mw-prod-githubrunners-eastus2-a'

@description('(Optional) The version of the .NET frameworks CLR used in this App Service. Possible values are v2.0 which will use the latest version of the .NET framework for the .NET CLR v2 - currently .net 3.5, v4.0 which corresponds to the latest version of the .NET CLR v4 - which at the time of writing is .net 4.7.1), v5.0 and v6.0.Defaults to v4.0.')
param funcNetFrameworkVersion string = 'v8.0'

@description('true to use 32-bit worker process; otherwise, false.')
param funcUse32BitWorkerProcess bool = false

@description('(Optional) Name of connection string, Connection value, and Type of database. For Example: ApiHub,Custom,DocDb,EventHub,MySql,NotificationHub,PostgreSQL,RedisCache,SQLAzure,SQLServer,ServiceBus. ')
param funcConnectionStrings array = []

@description('(Optional) IP security restrictions for scm to use main.')
param funcScmIpSecurityRestrictionsUseMain bool = true

@description('BA/QA function parameters to connect to OpenAI API')
param openaiUrl string
param openaiCId string
param openaiSv string
param openaiCrScope string
param openaiDeplName string
param openaiTenId string

// Function App - Storage Account Optional Parameters
//*****************************************************************************************************
@description('(Optional) Type of managed service identity.')
param stIdentityType string = 'SystemAssigned'

@description('(Optional) Gets or sets the SKU name. ')
param stSku string = 'Standard_LRS'

@description('(Optional) Required. Indicates the type of storage account.')
param stkind string = 'StorageV2'

@description('(Optional) Specifies whether traffic is bypassed for Logging/Metrics/AzureServices. Possible values are any combination of Logging,Metrics,AzureServices (For example, "Logging, Metrics"), or None to bypass none of those traffics.')
@allowed([
  'AzureServices'
  'None'
])
param stAclBypass string = 'None'

@description('(Optional) Specifies the default action of allow or deny when no other rules match.')
@allowed([
  'Allow'
  'Deny'
])
param stAclDefaultAction string = 'Deny'

@description('(Optional)Sets the IP ACL rules')
param stAclipRule array = []

@description('(Optional) Sets the virtual network rules')
#disable-next-line no-unused-vars no-unused-params
param stVirtualNetworkRules array = []
//*****************************************************************************************************


// Predefined Function App  Variables
//*****************************************************************************************************
var funcMintlsversion = '1.2'
var funcScmMinTlsVersion = '1.2'
var funcHttpsOnly= true
// var stConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
var funcVnetRouteAllEnabled = true

// Predefined Function App Storage Account Variables
//*****************************************************************************************************
var stAllowBlobPublicAccess = false
var stHttpsTrafficOnly = true
var stIsLocalUserEnabled = false
var stTlsVersion = 'TLS1_2'
var stFtpEnabled = false
var funcVnets = [ any(funcVnetintId) ]
//*****************************************************************************************************


// Function App - Storage Account  Resource
//*****************************************************************************************************
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: replace(stName, '-', '')
  location: region
  tags: tags
  sku: {
    name: stSku
  }
  kind: stkind
  identity: {
    type: stIdentityType
  }
  properties: {
    allowBlobPublicAccess: stAllowBlobPublicAccess
    supportsHttpsTrafficOnly: stHttpsTrafficOnly
    isLocalUserEnabled: stIsLocalUserEnabled
    minimumTlsVersion: stTlsVersion
    isSftpEnabled: stFtpEnabled
    allowSharedKeyAccess: true
    networkAcls: {
      bypass: stAclBypass
      defaultAction: stAclDefaultAction
      ipRules: stAclipRule
      virtualNetworkRules: [for id in funcVnets: {
        action: 'Allow'
        id: id
      }]
    }    
  }

  resource fileService 'fileServices@2023-01-01' = {
    name: 'default'

    resource fileServiceShare 'shares@2023-01-01' = {
      name: sys.take('${funcName}-content', 63)
    }
  }

  resource blobService 'blobServices@2023-01-01' = {
    name: 'default'
    properties: {
      deleteRetentionPolicy: {
        enabled: true
        days: 7
      }
      containerDeleteRetentionPolicy: {
        enabled: true
        days: 7
      }
    }
  } 
}
//*****************************************************************************************************


// Function App Resource
//*****************************************************************************************************
resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: funcName
  location: region
  kind: funcKind
  identity: {
    type: funcIdentityType
    userAssignedIdentities: (funcIdentityType == 'UserAssigned' || funcIdentityType == 'SystemAssigned, UserAssigned') ? {
      '${funcUserAssignedId}': {}
    } : null
  }
  properties: {
    serverFarmId: funcAspId
    virtualNetworkSubnetId: funcVnetintId
    httpsOnly: funcHttpsOnly
    vnetRouteAllEnabled: funcVnetRouteAllEnabled
    vnetContentShareEnabled: true
    publicNetworkAccess: (empty(SubnetResourceIdsForServiceEndpoints)) ? 'Disabled' : 'Enabled'
        
    siteConfig: {
      alwaysOn: funcAlwayson
      ftpsState: funcFtpsState
      minTlsVersion: funcMintlsversion
      scmMinTlsVersion: funcScmMinTlsVersion
      netFrameworkVersion: funcNetFrameworkVersion
      use32BitWorkerProcess: funcUse32BitWorkerProcess
      publicNetworkAccess: (empty(SubnetResourceIdsForServiceEndpoints)) ? 'Disabled' : 'Enabled'
      ipSecurityRestrictionsDefaultAction: (empty(SubnetResourceIdsForServiceEndpoints)) ?  null : 'Deny'
      scmIpSecurityRestrictionsDefaultAction: (empty(SubnetResourceIdsForServiceEndpoints)) ?  null : 'Deny'
      scmIpSecurityRestrictionsUseMain: funcScmIpSecurityRestrictionsUseMain
      cors: {
        allowedOrigins:[
          'https://oryx-cdn.microsoft.io'
          'https://functions-next.azure.com'
          'https://functions-staging.azure.com'
          'https://functions.azure.com'
          'https://portal.azure.com'
  
        ]
      }
      scmIpSecurityRestrictions: [
        { action: funcipSecurityRestrictionAction          
          priority: 901
          name: 'Github Runner Dev'          
          description: funcIpSecurityRestrictionDescription          
          vnetSubnetResourceId: githubsunetdevId        
        }
        {
          action: funcipSecurityRestrictionAction
          priority: 902
          name: 'Github Runner Prod'
          description: funcIpSecurityRestrictionDescription
          vnetSubnetResourceId: githubsunetprodId
        }
        {
          action: funcipSecurityRestrictionAction
          priority: 900
          name: funcIpSecurityRestrictionName
          description: funcIpSecurityRestrictionDescription
          vnetSubnetResourceId: SubnetResourceIdsForServiceEndpoints
        }
        {
          ipAddress: 'AzureDevOps'
          tag: 'ServiceTag'
          action: funcipSecurityRestrictionAction
          priority: 800
          name: 'ADO-TO-AZ'
        }
        {
          ipAddress: 'AzureCloud'
          tag: 'ServiceTag'
          action: funcipSecurityRestrictionAction
          priority: 700
          name: 'AzureCloudAccess'
        }
      ]
      ipSecurityRestrictions: [
        {
          action: funcipSecurityRestrictionAction
          priority: 901
          name: 'Github Runner Dev'
          description: funcIpSecurityRestrictionDescription
          vnetSubnetResourceId: githubsunetdevId
        }
        {
          action: funcipSecurityRestrictionAction
          priority: 902
          name: 'Github Runner Prod'
          description: funcIpSecurityRestrictionDescription
          vnetSubnetResourceId: githubsunetprodId
        }
        {
          action: funcipSecurityRestrictionAction
          priority: 900
          name: funcIpSecurityRestrictionName
          description: funcIpSecurityRestrictionDescription
          vnetSubnetResourceId: SubnetResourceIdsForServiceEndpoints
        }
        {
          ipAddress: 'AzureDevOps'
          tag: 'ServiceTag'
          action: funcipSecurityRestrictionAction
          priority: 800
          name: 'ADO-TO-AZ'
        }
        {
          ipAddress: 'AzureCloud'
          tag: 'ServiceTag'
          action: funcipSecurityRestrictionAction
          priority: 700
          name: 'AzureCloudAccess'
        }
      ]
      linuxFxVersion: 'PYTHON|3.11'
      //linuxFxVersion: contains(funcKind, 'linux') ? '${toUpper(funcWorkerRuntimeString)}|${replace(funcNetFrameworkVersion,'v','')}' : null
      connectionStrings: funcConnectionStrings
    }
  }
  tags: tags
  dependsOn: [
    storageAccount
  ]
}
//*****************************************************************************************************

// app settings - prevents complete replace of *all* app settings, and is incremental
var stConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'

resource functionAppAppSettings 'Microsoft.Web/sites/config@2023-01-01' = {
  name: 'appsettings'
  parent: functionApp
  properties: {
        AzureWebJobsStorage: stConnectionString
        WEBSITE_CONTENTAZUREFILECONNECTIONSTRING: stConnectionString 
        WEBSITE_CONTENTSHARE: storageAccount::fileService::fileServiceShare.name
        FUNCTIONS_EXTENSION_VERSION: '~4'
        WEBSITE_NODE_DEFAULT_VERSION: '~14'
        APPLICATIONINSIGHTS_CONNECTION_STRING: funcAppiConnectionString
        ApplicationInsightsAgent_EXTENSION_VERSION: '~2'
        FUNCTIONS_WORKER_RUNTIME: funcWorkerRuntimeString
        XDT_MicrosoftApplicationInsights_Mode: 'Recommended'
        openai_api_base: openaiUrl
        openai_client_id: openaiCId
        openai_client_secret: openaiSv
        openai_credential_scope: openaiCrScope
        openai_deployment_name: openaiDeplName
        openai_tenant_id: openaiTenId
        SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
        BUILD_FLAGS: 'UseExpressBuild'
        ENABLE_ORYX_BUILD: 'true'
        WEBSITE_RUN_FROM_PACKAGE: '1'
        // WEBSITE_CONTENTOVERVNET:'1'
        // WEBSITE_VNET_ROUTE_ALL: '1'
      }
    }

// Outputs Function App
//*****************************************************************************************************
output functionAppName string = functionApp.name
output functionId string = functionApp.id
output functionIdentityId string = functionApp.identity.principalId
output functionStName string = storageAccount.name
output functionStId string = storageAccount.id
//*****************************************************************************************************
