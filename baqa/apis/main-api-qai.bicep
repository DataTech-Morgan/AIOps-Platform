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
var policy_qai = 'policy'

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
  name: policy_qai
  properties: {
    //value: '<!--- Policies are applied in the order they appear.- Position <base/> inside a section to inherit policies from the outer scope.- Comments within policies are not preserved.--><!-- Add policies as children to the <inbound>, <outbound>, <backend>, and <on-error> elements --><policies><!-- Throttle, authorize, validate, cache, or transform the requests --><inbound><validate-jwt header-name="Authorization" failed-validation-httpcode="401" failed-validation-error-message="Unauthorized. Access token is missing or invalid." require-expiration-time="true" require-scheme="Bearer" require-signed-tokens="true" output-token-variable-name="jwt"><openid-config url="https://sts.windows.net/e2ba673a-b782-4f44-b0b5-93da90258200/.well-known/openid-configuration" /><audiences><audience>${audience}</audience></audiences><issuers><issuer>https://sts.windows.net/e2ba673a-b782-4f44-b0b5-93da90258200</issuer></issuers><required-claims><claim name="roles" match="any"><value>${policy_role}</value></claim></required-claims></validate-jwt><!--Decode process--><set-variable name="azpValue" value="@(context.Request.Headers.GetValueOrDefault("Authorization").AsJwt()?.Claims.GetValueOrDefault("azp"))" /><!--Azp value to the request header --><set-header name="ClientId" exists-action="override"><value>@((string)context.Variables["azpValue"])</value></set-header><choose><when condition="@(((Jwt)context.Variables["jwt"]).Claims["roles"].Contains("${policy_role}"))"><set-variable name="credentials" value="{{api-admin-credentials}}" /></when></choose><choose><when condition="@(context.Variables.GetValueOrDefault&lt;string&gt;("credentials","") == "")"><return-response><set-status code="401" reason="Unauthorized" /></return-response></when><otherwise><set-header name="x-thirdparty-token" exists-action="override"><value>@(context.Variables.GetValueOrDefault&lt;string&gt;("credentials"))</value></set-header></otherwise></choose><set-header name="Ocp-Apim-Subscription-Key" exists-action="delete" /><base /><authentication-managed-identity resource="https://cognitiveservices.azure.com" /></inbound><!-- Control if and how the requests are forwarded to services  --><backend><base /></backend><!-- Customize the responses --><outbound><base /><set-header name="Access-Control-Allow-Origin" exists-action="append"><value>*</value></set-header></outbound><!-- Handle exceptions and customize error responses  --><on-error><base /></on-error></policies>'
    value: loadTextContent('./policies/uat/uat.funcapppolicy.xml')
    format: 'rawxml'
  }
}

resource apiOperations2 'Microsoft.ApiManagement/service/apis/operations@2023-03-01-preview' = {
  parent: apiConfiguration
  name: 'get-testcaseqai'
  properties: {
    displayName: 'testcaseQai'
    method: 'GET'
    urlTemplate: '/testcaseQai'
    templateParameters: [
    ]
    request: {
    }
    responses: [
    ]
  }
}
resource polOperations2 'Microsoft.ApiManagement/service/apis/operations/policies@2023-03-01-preview' = {
  name: 'policy'
  parent: apiOperations2
  properties: {
    format: 'xml'
    value: '<policies><inbound><base /><set-backend-service id="apim-generated-policy" backend-id="${apiBackendName}" /></inbound><backend><base /></backend><outbound><base /></outbound><on-error><base /></on-error></policies>'
  }
}

resource apiOperations3 'Microsoft.ApiManagement/service/apis/operations@2023-03-01-preview' = {
  parent: apiConfiguration
  name: 'post-testcaseqai'
  properties: {
    displayName: 'testcaseQai'
    method: 'POST'
    urlTemplate: '/testcaseQai'
    templateParameters: [
    ]
    request: {
    }
    responses: [
    ]
  }
}
resource polOperations3 'Microsoft.ApiManagement/service/apis/operations/policies@2023-03-01-preview' = {
  name: 'policy'
  parent: apiOperations3
  properties: {
    format: 'xml'
    value: '<policies><inbound><base /><set-backend-service id="apim-generated-policy" backend-id="${apiBackendName}" /></inbound><backend><base /></backend><outbound><base /></outbound><on-error><base /></on-error></policies>'
  }
}



