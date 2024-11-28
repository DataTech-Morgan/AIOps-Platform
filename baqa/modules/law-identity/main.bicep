
param lawName string
param varRoleAssignmentAppiId string
param AppiInsightsprincipalId string
param varAppiLogContributor string

resource existingLAW 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: lawName
}

resource authorizationApim 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: varRoleAssignmentAppiId
  scope: existingLAW
  properties: {
    principalId: AppiInsightsprincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: varAppiLogContributor
  }
}
