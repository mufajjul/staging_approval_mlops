# <az_ml_install>
az extension add -n ml -y
# </az_ml_install>

# rc install - uncomment and adjust below to run all tests on a CLI release candidate
#z extension remove -n ml
#az extension add --source https://azuremlsdktestpypi.blob.core.windows.net/wheels/sdk-cli-v2-public/ml-2.2.1-py3-none-any.whl --yes
 
# <set_variables>
GROUP="mlstudio"
LOCATION="eastus"
WORKSPACE="aml-cust-demo"
# </set_variables>

# <az_configure_defaults>
az configure --defaults group=$GROUP workspace=$WORKSPACE location=$LOCATION
# </az_configure_defaults>