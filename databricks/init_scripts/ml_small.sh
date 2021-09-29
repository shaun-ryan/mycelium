#!/bin/bash

export ENVIRONMENT=DEV
export AZUREADID=a69c8df4-e648-4b0a-beb9-b3716a01f60e
export LOGAPPALERTEMAIL=shaun_chibru@hotmail.com
export AUTOMATIONSCOPE=azure-key-vault-scope
export STORAGE=AzureDataLakeGen2
export STORAGEACCOUNT=abfss://datalake@datalakegeneva.dfs.core.windows.net/
export RESOURCEGROUP=DataPlatform
export SUBSCRIPTIONID=e95203c2-64a0-43f9-bfc5-a4fdc588571a
export LOGAPPALERTENDPOINT=LOGAPP-ALERT-ENDPOINT
export DATAPLATFORMAPPID=DATALAKE-SPN-APPID
export DATAPLATFORMSECRET=DATALAKE-SPN-CREDENTIAL
export LOGGINGLEVELOVERRIDE=ERROR
export PIPELINEPROJECTSDIR=/dbfs/FileStore/pipelineProjects/

pip install /dbfs/FileStore/deployment/wheels/mycelium.whl
/databricks/python/bin/pip install install autobricks