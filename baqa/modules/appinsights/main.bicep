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


// Required Parameters Application Insights
//*****************************************************************************************************
@maxLength(255)
param appiName string

@description('The ID of Log Analytics Workspace.')
param workspaceId string
//*****************************************************************************************************


// Optional Parameters Application Insights
//*****************************************************************************************************
@description('(Optional) The kind of application that this component refers to, used to customize UI. This value is a freeform string, values should typically be one of the following: web, ios, other, store, java, phone.')
@allowed([
  'web'
  'ios'
  'other'
  'store'
  'java'
  'phone'
])
param appiKind string = 'web'

@description('(Optional)Type of application being monitored.')
@allowed([
  'web'
  'other'
])
param appiAppType string = 'web'

@description('(Optional) Used by the Application Insights system to determine what kind of flow this component was created by. This is to be set to Bluefield when creating/updating a component via the REST API.')
param appiFlowType string = 'Bluefield'

@description('(Optional) Used by the Application Insights system with local authentication for use case not supported.')
param appiInstKeyEnabled bool = false
//*****************************************************************************************************

//Required paramaters Appi Test
//*****************************************************************************************************
 @description('APIM url to test')
 param apimurltest string

@description('Action Group Name')
param appiAGName string = 'Application Insights Smart Detection'
param appiAGShortName string = 'SmartDetect'

// @description('webhookURL to metrics monitoring')
// param webhookURL string

// Application Insights Resource
//*****************************************************************************************************
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appiName
  location: region
  tags: tags
  kind: appiKind
  properties: {
    Application_Type: appiAppType
    WorkspaceResourceId: workspaceId
    Flow_Type: appiFlowType
    DisableLocalAuth: appiInstKeyEnabled ? false : true
  }
}

var appitesttag = applicationInsights.id
//*****************************************************************************************************

//API Test APPI
//*****************************************************************************************************
resource appitest 'Microsoft.Insights/webtests@2022-06-15' = {
  name: appiName
  location: region
  tags: {
    'hidden-link:${appitesttag}': 'Resource'
  }
  kind: 'standard'
  properties: {
    SyntheticMonitorId: appiName
    Name: appiName
    Description: 'APIM availability test'
    Enabled: true
    Frequency: 300
    Timeout: 30
    Kind: 'standard'
    RetryEnabled: true
    Locations: [
      {
        Id: 'us-va-ash-azr'
      }
      {
        Id: 'us-ca-sjc-azr'
      }
    ]
    Configuration: null
    Request: {
      RequestUrl: apimurltest
      Headers: null
      HttpVerb: 'GET'
      RequestBody: null
      ParseDependentRequests: false
      FollowRedirects: null
    }
    ValidationRules: {
      ExpectedHttpStatusCode: 200
      IgnoreHttpStatusCode: false
      ContentValidation: null
      SSLCheck: true
      SSLCertRemainingLifetimeCheck: 7
    }
  }
}

resource actionGroup 'Microsoft.Insights/actionGroups@2021-09-01' = {
  name: appiAGName
  location: 'Global'
  properties: {
    groupShortName: appiAGShortName
    enabled: true
    smsReceivers: []
    emailReceivers: []
    // webhookReceivers: [
    //   {
    //     name: 'EventMgmt'
    //     serviceUri: webhookURL
    //     useCommonAlertSchema: true
    //     useAadAuth: false
    //     objectId: null
    //     identifierUri: null
    //     tenantId: null
    //   }
    // ]
    eventHubReceivers: []
    itsmReceivers: []
    azureAppPushReceivers: []
    automationRunbookReceivers: []
    voiceReceivers: []
    logicAppReceivers: []
    azureFunctionReceivers: []
    armRoleReceivers: []
  }
}

resource metricAlertAvailabilityTest 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: appiName
  location: 'global'
  properties: {
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.WebtestLocationAvailabilityCriteria'
      componentId: applicationInsights.id
      failedLocationCount: 2
      webTestId: appitest.id
    }
    description: 'Automatically created alert rule for availability test'
    enabled: true
    evaluationFrequency: 'PT1M'
    scopes: [
      appitest.id
      applicationInsights.id
    ]
    severity: 1
    windowSize: 'PT5M'
  }
}


// Outputs Application Insights
//*****************************************************************************************************
output appiId string = applicationInsights.id
output appiName string = applicationInsights.name
output appiIntConString string = applicationInsights.properties.ConnectionString
//*****************************************************************************************************

