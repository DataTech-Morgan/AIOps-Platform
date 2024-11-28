// Function App APIs and operations deployment

/*parameters*/
@allowed([
  'dev'
  'stg'
  'uat'
  'prod'
])
param environment string

@allowed([
  'mw'
  'to'
])
param businessDirectory string

param azureServ string
param apiname string
param apimSuffix string
param apiType string
param apidescription string
param apidispname string
param version string
// param tagging string
param apiBackendName string
param backendurl string
param loggerId string

/*policy parameters*/
//param audience string
//param policy_role string


/*variable*/
var varApimName = 'apim-${businessDirectory}-${environment}-${apimSuffix}'
var pathAPI = '${azureServ}/${version}'
// var taggings = tagging
var policy_feedback = 'policy'

resource apimanagement 'Microsoft.ApiManagement/service@2021-08-01' existing = {
  name: varApimName
}

resource apibackend 'Microsoft.ApiManagement/service/backends@2023-03-01-preview' = {
  parent: apimanagement
  name: apiBackendName
  properties: {
    description: apiBackendName
    url: backendurl
    protocol: 'http'
  }
}

/*API setup*/
resource apiConfiguration 'Microsoft.ApiManagement/service/apis@2023-03-01-preview' = {
  name: apiname
  parent: apimanagement
  properties: {
    apiType: apiType
    displayName: apidispname
    description: apidescription
    subscriptionRequired: false
    path: pathAPI
    protocols: [
      'https'
    ]
    subscriptionKeyParameterNames: {
      header: 'Ocp-Apim-Subscription-Key'
      query: 'subscription-key'
    }
  }
}


resource diagsettings 'Microsoft.ApiManagement/service/apis/diagnostics@2023-03-01-preview' = {
  name: 'applicationinsights'
  parent: apiConfiguration
  properties: {
    alwaysLog: 'allErrors'
    backend: {
      request: {
        body: {
          bytes: 0
        }
        headers: [
          'ClientId'
        ]
      }
    }
    httpCorrelationProtocol: 'Legacy'
    logClientIp: true
    loggerId: loggerId
    verbosity: 'information'
  }
}

resource apimNamedValue 'Microsoft.ApiManagement/service/namedValues@2021-08-01' = {
  parent: apimanagement
  name: 'api-admin-credentials'
  properties: {
    displayName: 'api-admin-credentials'
    value: 'none'
    secret: true
  }
}

resource service_apim_post_secured_policies_bai 'Microsoft.ApiManagement/service/apis/policies@2023-03-01-preview' = {
  parent: apiConfiguration
  name: policy_feedback
  properties: {
    value: loadTextContent('./policies/uat/uat.funcapppolicy.xml')
    format: 'rawxml'
  }
}

resource apiOperations4 'Microsoft.ApiManagement/service/apis/operations@2023-03-01-preview' = {
  parent: apiConfiguration
  name: 'post-feedbackBai'
  properties: {
    displayName: 'feedbackBai'
    method: 'POST'
    urlTemplate: '/feedbackBai'
    templateParameters: [
    ]
    request: {
    }
    responses: [
    ]
  }
}
resource polOperations4 'Microsoft.ApiManagement/service/apis/operations/policies@2023-03-01-preview' = {
  name: 'policy'
  parent: apiOperations4
  properties: {
    format: 'xml'
    value: '<policies><inbound><base /><set-backend-service id="apim-generated-policy" backend-id="${apiBackendName}" /></inbound><backend><base /></backend><outbound><base /></outbound><on-error><base /></on-error></policies>'
  }
}
