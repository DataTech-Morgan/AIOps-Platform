// Create RG with specific tags

/* Parameters */
@maxLength(64)
param ResourceNameSuffix string
param ApplicationName string

@allowed([
  'eastus'
  'eastus2'
  'westus'
  'westus2'
])
param Region string

param SNOWApplicationName string
param SNOWBASysID string
param SNOWBU string
param SNOWBusinessCriticality string
param SNOWDataClassification string
param SNOWOwner string
param SNOWValueStream string
param appName string
param Recovery string
param ServiceLevel string

@allowed([
'dev'
'stg'
'uat'
'prod'
])
@maxLength(4)
param Environment string

/* Variables */
var varresourceName = 'rg-mw-${Environment}-${appName}-${ResourceNameSuffix}'
targetScope = 'subscription'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: varresourceName
  location: Region
  tags: {
    ApplicationName: ApplicationName
    Environment: Environment
    Recovery: Recovery
    ServiceLevel: ServiceLevel
    SNOWApplicationName: SNOWApplicationName
    SNOWBASysID: SNOWBASysID
    SNOWBU: SNOWBU
    SNOWBusinessCriticality: SNOWBusinessCriticality
    SNOWDataClassification: SNOWDataClassification
    SNOWOwner: SNOWOwner
    SNOWvalueStream: SNOWValueStream
  }
}
