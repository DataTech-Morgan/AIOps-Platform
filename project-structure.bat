@echo off

REM Define the root project directory
set "root_dir=C:\Users\consbkb\OneDrive - JM Family Enterprises\Desktop\Personal\Repositories\AIOPS-MW\AI-MW-Applications"

REM Create rg  directories
mkdir "%root_dir%\resource-groups\1-Infrastructure\baqa\parameters\1-dev"
mkdir "%root_dir%\resource-groups\1-Infrastructure\baqa\parameters\2-uat"
mkdir "%root_dir%\resource-groups\1-Infrastructure\baqa\parameters\3-prod"
mkdir "%root_dir%\resource-groups\1-Infrastructure\sharedservices\parameters\1-dev"
mkdir "%root_dir%\resource-groups\1-Infrastructure\sharedservices\parameters\2-uat"
mkdir "%root_dir%\resource-groups\1-Infrastructure\sharedservices\parameters\3-prod"
mkdir "%root_dir%\resource-groups\2-modules\config"
mkdir "%root_dir%\resource-groups\2-modules\rg"
mkdir "%root_dir%\resource-groups\3-pipelines\baqa"
mkdir "%root_dir%\resource-groups\3-pipelines\sharedservice"

REM Create baqa resources directories
mkdir "%root_dir%\baqa\1-Infrastructure\backend\parameters\1-dev"
mkdir "%root_dir%\baqa\1-Infrastructure\backend\parameters\2-uat"
mkdir "%root_dir%\baqa\1-Infrastructure\backend\parameters\3-prod"
mkdir "%root_dir%\baqa\2-modules\config"
mkdir "%root_dir%\baqa\2-modules\functionapps"
mkdir "%root_dir%\baqa\2-modules\appserviceplan"
mkdir "%root_dir%\baqa\2-modules\appinsights"
mkdir "%root_dir%\baqa\2-modules\rbac"
mkdir "%root_dir%\baqa\2-modules\comosdb"
mkdir "%root_dir%\baqa\3-pipelines\backend"

REM Create api-management resources directories
mkdir "%root_dir%\api-management\1-infrastructure\apim\parameters\1-dev"
mkdir "%root_dir%\api-management\1-infrastructure\apim\parameters\2-uat"
mkdir "%root_dir%\api-management\1-infrastructure\apim\parameters\3-prod"
mkdir "%root_dir%\api-management\1-infrastructure\apim\policies\1-dev"
mkdir "%root_dir%\api-management\1-infrastructure\apim\policies\2-uat"
mkdir "%root_dir%\api-management\1-infrastructure\apim\policies\3-prod"
mkdir "%root_dir%\api-management\1-infrastructure\law\parameters\1-dev"
mkdir "%root_dir%\api-management\1-infrastructure\law\parameters\2-uat"
mkdir "%root_dir%\api-management\1-infrastructure\law\parameters\3-prod"
mkdir "%root_dir%\api-management\2-modules\apimanagement"
mkdir "%root_dir%\api-management\2-modules\apimanagement-logger"
mkdir "%root_dir%\api-management\2-modules\apimanagement-policy"
mkdir "%root_dir%\api-management\2-modules\config"
mkdir "%root_dir%\api-management\2-modules\appinsight"
mkdir "%root_dir%\api-management\2-modules\law"
mkdir "%root_dir%\api-management\2-modules\storage-account"
mkdir "%root_dir%\api-management\2-modules\rbac"
mkdir "%root_dir%\api-management\2-modules\publicip"
mkdir "%root_dir%\api-management\3-pipelines\apim"
mkdir "%root_dir%\api-management\3-pipelines\law"


REM Notify user of completion
echo Project structure has been created.
pause