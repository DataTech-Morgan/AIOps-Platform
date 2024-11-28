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


// Require Parameters App Service Plan
//*****************************************************************************************************
@description('(Require) The app name for the AppService Plan.')
@maxLength(40)
param aspName string
//*****************************************************************************************************


// App Service Plan Optional Parameters
//*****************************************************************************************************
@description('(Optional) Description of a SKU for a scalable resource.')
param aspSkuName string = 'S1'

@description('(Optional) Kind of resource.')
@allowed([ 
  'linux'
  'windows'
  'app'
  'elastic' 
  'xenon'
  'functionapp'
])
param aspKind string = 'linux'

@description('(Optional) Service tier of the resource SKU.')
@allowed([ 
  'Basic' 
  'Standard' 
  'PremiumV3' 
  'WorkflowStandard'
])
param aspSkuTier string = 'Standard'

@description('(Optional) Specifies the number of workers associated with this App Service Plan.')
param aspSkuCapacity int = 1

@description('(Optional) Specifies if the App Service Plan should be Zone Redundant.')
param aspZoneRedundant bool = false

param newOrExisting string
//*****************************************************************************************************


// App Service Plan Resource 
//*****************************************************************************************************
resource existingAppServicePlan 'Microsoft.Web/serverfarms@2022-03-01' existing = if (newOrExisting == 'existing') {
  name: aspName
}
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = if (newOrExisting == 'new') {
  name: aspName
  location: region
  kind: aspKind

  sku: {
    capacity: aspSkuCapacity
    name: aspSkuName
    tier: aspSkuTier
  } 
  
  properties: {
    isXenon: aspKind == 'xenon' ? true : false
    reserved: aspKind == 'linux' ? true : false
    zoneRedundant: aspSkuTier == 'PremiumV3' ? aspZoneRedundant : false
  }
  tags: tags
}
//****************************************************************************************************


// Outputs App Service Plan
//*****************************************************************************************************
@description('Output the farm id')
output aspId string = ((newOrExisting == 'new') ? appServicePlan.id : existingAppServicePlan.id)
@description('Output the farm id')
output aspName string = ((newOrExisting == 'new') ? appServicePlan.name : existingAppServicePlan.name)

//*****************************************************************************************************
