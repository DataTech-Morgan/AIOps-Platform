/*Parameters KeyVault*/
param location string = resourceGroup().location
param keyVaultName string 
param tenantId string = subscription().tenantId
param newOrExisting string
param tags object
param subnetBackEndIntegrationID string 

/* Variables */

/* Creating Resources*/
resource existingKeyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = if (newOrExisting == 'existing') {
  name: keyVaultName
}
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = if (newOrExisting == 'new') {
  name: keyVaultName
  location: location
  properties: {
    tenantId: tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    accessPolicies: [] // Access policies can be defined here
    networkAcls: {
      defaultAction: 'Deny'
      virtualNetworkRules: [
        {
          id: subnetBackEndIntegrationID
          ignoreMissingVnetServiceEndpoint: true
        }
      ]
    }
  }
  tags:tags
}

output kvId string = ((newOrExisting == 'new') ? keyVault.id : existingKeyVault.id)
output kvName string = ((newOrExisting == 'new') ? keyVault.name : existingKeyVault.name)
