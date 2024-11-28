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

@description('(Require) The business unit owning the resources.')
@allowed([
   'mw' 
   'to'
])
@maxLength(4)
param businessDirectory string 

@description('(Require) The deployment stage where the resources.')
@allowed([
   'dev'
   'stg' 
   'uat' 
   'prod' 
])
@maxLength(4)
param deploymentStage string 

@description('Application Name of the deployment')
param applicationName string

@description('Application ID of the deployment')
param applicationId string

@description('TAGs for the deployment')
param tags object

@description('App Insight parameters')
param workspaceId string
param roleAppiDefinitionResourceID string
param roleKeyVaultDefinitionID string

param apimurltest string
//*****************************************************************************************************

//*****************************************************************************************************

// App Service PLan Backend Services
//************************************************************************************************
@description('Role of the ASP deployment')
param appServicePlanFuncAppKind string

@description('SKU of the ASP deployment')
param appServicePlanfuncAppSKU string

@description('Tier of the ASP deployment')
param appServicePlanfuncAppTier string

//***********************************************************************************************

// Function App deployment
//*****************************************************************************************************

// Function App parameters
//***********************************************************************************************
@description('Subnet integration for ASP Backend')
param subnetBackEndIntegrationID string

@description('function App role')
param funcWorkerRuntimeString string
param productName string
param subnetcognitiveservID string

@description('BA/QA function parameters to connect to OpenAI API')
param tenantId string = subscription().tenantId
param openaiUrl string
param openaiCId string = '@Microsoft.KeyVault(SecretUri=https://kv-mw-${deploymentStage}-baqa-wkld-a.vault.azure.net/secrets/openaiClientId)'
param openaiSv string = '@Microsoft.KeyVault(SecretUri=https://kv-mw-${deploymentStage}-baqa-wkld-a.vault.azure.net/secrets/openaiClientSecret)'
param openaiCrScope string = '@Microsoft.KeyVault(SecretUri=https://kv-mw-${deploymentStage}-baqa-wkld-a.vault.azure.net/secrets/openaiCredentialScope)'
param openaiDeplName string
param openaiTenId string = '@Microsoft.KeyVault(SecretUri=https://kv-mw-${deploymentStage}-baqa-wkld-a.vault.azure.net/secrets/openaiTenantId)'

// RBAC APIM to Function App
// @description('Role APIM to the Function App and APIM principal Id')
// param roleFuncAppDefinitionResourceID string
// param APIManagementName string
// param principalIdAPIM string

param newOrExisting string

/* Variables*/
var aspName = 'asp-${businessDirectory}-${deploymentStage}-${applicationName}-${applicationId}'
var funcappName = 'func-${businessDirectory}-${deploymentStage}-${applicationName}-${productName}-${applicationId}'
var appinsightsName = 'appi-${businessDirectory}-${deploymentStage}-${applicationName}-${applicationId}'
var stName = 'st${businessDirectory}${deploymentStage}${productName}wkl${applicationId}'
var keyvaultName = 'kv-${businessDirectory}-${deploymentStage}-baqa-wkld-${applicationId}'
// var rglawName = 'rg-${businessDirectory}-${deploymentStage}-ai-products-sharedlog-a'
// var subslawName = 'sb-${businessDirectory}-${deploymentStage}-ai-products-platform-a'
// var lawName = 'law-${businessDirectory}-${deploymentStage}-ai-products-sharedlog-a'

var varRoleAssignmentAppiId = guid('role-assignment-${productName}',deploymentStage, '-', resourceId('Microsoft.ApiManagement/sites', funcappName))
var varAppiLogContributor = resourceId('Microsoft.Authorization/roleDefinitions',roleAppiDefinitionResourceID)

var varRoleAssignmentKeyVaultId = guid('roleassignmentKV-',deploymentStage, '-', resourceId('Microsoft.Web/sites', funcappName))
var varKeyVaultSecretsUser = resourceId('Microsoft.Authorization/roleDefinitions',roleKeyVaultDefinitionID)

// BEGIN Infrastructure Declaration
//*****************************************************************************************************

// Azure Key Vault 
// *****************************************************************************************************

module keyvaultbaqa '../../modules/keyvault/main.bicep' = {
  name: 'azurekeyvault'
  params: {
    keyVaultName: keyvaultName
    location: region
    tenantId: tenantId
    newOrExisting: newOrExisting
    tags: tags
    subnetBackEndIntegrationID: subnetBackEndIntegrationID
  }
}

// App Service Plan - BackEnd 
//*****************************************************************************************************

module appServicePlanBackEnd '../../modules/appserviceplan/main.bicep' = {
  name: 'appServicePlanBakd'
  params: {
    aspName: aspName
    region: region
    aspKind: appServicePlanFuncAppKind
    aspSkuName: appServicePlanfuncAppSKU
    aspSkuTier: appServicePlanfuncAppTier
    newOrExisting: newOrExisting
    tags: tags
  }
}
//*****************************************************************************************************

// Function App Consume deployment
//******************************************************************************************************

// App Insights - Function App Consum
//*****************************************************************************************************
module appInsightsConsum '../../modules/appinsights/main.bicep' = {
  name: 'appInsightsConsum'
  params: {
    appiName: appinsightsName
    region: region
    workspaceId: workspaceId
    appiInstKeyEnabled: true
    tags: tags
    apimurltest: apimurltest
  }
}
//*****************************************************************************************************


module functionAppConsum '../../modules/functionapps/main.bicep' = {
  dependsOn: [appInsightsConsum, appServicePlanBackEnd]
  name: 'functionAppConsum'
  params: {
    funcName: funcappName
    stName: stName
    region: region
    funcAspId: appServicePlanBackEnd.outputs.aspId
    funcVnetintId: subnetBackEndIntegrationID
    SubnetResourceIdsForServiceEndpoints: subnetcognitiveservID
    funcWorkerRuntimeString: funcWorkerRuntimeString
    funcAppiConnectionString: appInsightsConsum.outputs.appiIntConString
    funcKind: 'functionapp,linux'
    // githubSubnetDevIpAdress: '10.231.2.32/27'
    // githubSubnetProdIpAdress: '10.231.2.0/27'
    // stVirtualNetworkRules: [
    //   {
    //     action: 'Allow'
    //     id: subnetcognitiveservID
    //   }
    // ]
    tags: tags
    openaiUrl: openaiUrl
    openaiCId: openaiCId
    openaiSv: openaiSv
    openaiCrScope: openaiCrScope
    openaiDeplName: openaiDeplName
    openaiTenId: openaiTenId
  }
}
//*****************************************************************************************************

// Role Assigment Log Analytics contributor to Application Insights - Function App Consum
//*****************************************************************************************************

resource existingAppiInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appinsightsName

}

resource authorizationAppi 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: varRoleAssignmentAppiId
  scope: existingAppiInsights
  properties: {
    principalId: functionAppConsum.outputs.functionIdentityId
    principalType: 'ServicePrincipal'
    roleDefinitionId: varAppiLogContributor
  }
}

resource exisitingKeyVault 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyvaultName
}
resource authorization 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: varRoleAssignmentKeyVaultId
  scope: exisitingKeyVault
  properties: {
    principalId: functionAppConsum.outputs.functionIdentityId
    principalType: 'ServicePrincipal'
    roleDefinitionId: varKeyVaultSecretsUser
  }
}


