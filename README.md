# AML Asset (Model) Stages and Approval MlOps 

# Motivation

1. As an ML Professional I want to be able to indicate which of the assets (model, dataset, environment and components) in the aml registry are in draft vs ready for review/approval (out of scope for current spec) to be moved to production. When an asset is ready to go to production, I should just be able to update the state/status and some other business process kicks off that I don’t need to know about in depth.

3. As a model/asset risk officer , when an ML professional marks a asset as ready for review I should be alerted and be able to drill into to review and approve.  For example, for a model, this would include being able to determine which project templates (if any) were used, which base models or features were used, and have full access to the code, the model, the data and the explanations / interpretability details that are available to facilitate Model Approval tracking. Further, I would like to be able to design a workflow which enforces my policies / validates my requirements have been met.
  

# Benefits

This feature provides the following benefits:

- Provide etter governance around the AML assets for enterprises.
- Use pre-build asset lifecycle to facilitate MLOPs deployment.
- Define custom stages for business specific lifecycle.
- Track stages change/lineage for assets
- Stage change event driven business specific workflow (logic apps, etc)
- Policy based lifecycle stages flow enforcement
- Use MlFlow SDK/Client extension to manage the asset stages (current supports model with pre-built stages)
- Advance access control on assets based on the lifecycle stage.

## Asset Stages Lifecycle

An asset lifecycle consists of a series of stages it undertakes during the MLOPs process to ensure that flow of execution/operation is perform in a certain order, be able to track the historical order of changes/updates and be able to perform various business processes or validation on change of stage, as well as to meet various regulatory and compliance requirements (see below).

![Screenshot 2022-07-05 at 11 48 43](https://user-images.githubusercontent.com/3224778/177311712-90d5b3bc-f7a2-4781-b440-cb64a5711a84.png)


E.g, adding the property here for a model: https://docs.microsoft.com/en-us/rest/api/azureml/model-versions

![](/docs/media/model-flow.png)


## What AML Assets are in Consideration?

1. Model
2. Dataset
3. Environment
4. Compoment


# Asset Staging

**Workspace and Registry will have asset stages.**

**Asset stages will apply to Single or Multiple (i.e.,Dev, Test and Prod) Workspaces.**

## Natively Supported Asset Lifecycle

AML to support None, Staging, Production, Archived to correspond with MLflow specification for Stages. In addition a special Stage called “Unregistered” is supported on which policies can be defined.

Unregistered == ["Unregistered Stage" <- not the real name]
Registered == [None, Staging, Production, Archived] == MLflow stages

There will be default policies enforcing only forward transitions to Stages. Customers can disable the default policies, for example, in order to move from Production to Staging if required. If required, customer should be able to create custom policies on any supported Stages.

The Four transitional stages are: None, Staging, Production and Archive.

0. **Unregistered(Special)**
   
   - Any transition from Unregistered will not be allowed. Customers will only be able to create/register other assets using Unregistered as a source. Only way to get rid of unregistered asset is to delete that asset.
   - Transition from [None, Staging, Prod, Archive] to Unregistered is not allowed.
   - Users can’t create asset with the Stage “Unregistered”
   - Only the AML system can auto create a model with Stage “Unregistered”. By definition, these can’t be versioned.   - When an asset in Unregistered stage is Registered by the customer, the stage is updated to None as part of the registration.   
1. **None**
   
   - c An asset in a "None" stage is the beginning of the lifecycle. This is considered to be a production ready asset.
   - An asset can be moved to the next stage (with optional approval process).
2. **Staging**
   
   - An asset in a "Staging" stage is ready to be moved into production. Various activities can be performed on the asset in a non-prod environment.
   - There should be an approval process for any resource moving out of Production also since it will be an impacting transition?
3. **Production**
   
   - An asset in the "Production" stage is ready to be deployed in a production environment. If there is an asset (model) already in production, this would automatically be moved to archive.
   - There should be an approval process for any resource moving out of Production also since it will be an impacting transition?
   - 
4. **Archive** - An asset in the "Archive" stage is the end of the lifecycle. The asset is no longer considered as production ready. Archiving will be consistent with how we archive assets in AzureML today. An archive asset is just hidden from the UI list and will be given the stage archive.

# MLFlow Parity

- The default Stages are quite similar to what we see in MlFlow, and this was done in
  purpose to make sure we are inline with MlFlow.
- MLflow transition_model_version_stage arg, which implies that transition of an asset might end up affecting all other existing versions

[https://www.mlflow.org/docs/latest/python_api/mlflow.tracking.html#mlflow.tracking.MlflowClient.transition_model_version_stage](https://www.mlflow.org/docs/latest/python_api/mlflow.tracking.html#mlflow.tracking.MlflowClient.transition_model_version_stage)






## Policies

Various policies are required to govern and manage the stages lifecycle.  This includes, what is the starting stage, end stage, and intermediaries, various operation that can and cannot be performed and the order it is performed.   Below is a list of candidate policies.

1. An asset can transit from one state to another (direct acyclic).
   i.e, None -> Staging,   staging -> production.
2. An asset can only be deleted in None or Archive stage (not in Staging or Production)
3. A deployment cannot be created if a model is in “None” or “Archive” stage.  (Applicable to Managed Endpoint).
4. A risk owner(s) or pre-selected users can only approve an asset transition (if approval is enabled).  (RBAC)

Enforceable Transition Patterns

Only using the AML registry for all assets (preferred)

•Mode: Resource propagation  (asset X: v1 – stage: None -> asset X:v1 - stage: Staging -> asset X: v1 - stage: production -> asset X: v1: Archive)  (a single version of asset, but updated stage property depending on where it is in the lifecycle).

•Mode: Resource evolution (retraining model) (asset X: v1 – stage: None -> asset X:v2 - stage: Staging -> asset X: v3 - stage: production -> asset X: v3: Archive)  (multiple versions of same asset at different stages,  and updated stage property depending on where it is in the lifecycle).

**Using both workspace and AML registry**

Azure policy allows used to run operations on the following properties:

Microsoft.MachineLearningServices/workspaces/models/tags
Microsoft.MachineLearningServices/workspaces/models/versions/datastoreId
Microsoft.MachineLearningServices/workspaces/models/versions/description
Microsoft.MachineLearningServices/workspaces/models/versions/flavors
Microsoft.MachineLearningServices/workspaces/models/versions/isAnonymous
Microsoft.MachineLearningServices/workspaces/models/versions/path
Microsoft.MachineLearningServices/workspaces/models/versions/tags

We need a new one for asset stages
Microsoft.MachineLearningServices/workspaces/*/stages

---

---

# Model Stage And Approval Lifecycle Demo

In this demo we are going to demonstrate Model Stages and Approval lifecycle for event based MlOPs. We are going to use the IRIS dataset to build a classification model to illustrate the end-to-end flow. This example will use CLI V2.

Here are the list of steps we are going to follow:

1. How to create Azure Policies for stages and approval lifecycle
2. How to assign policies at the resource group level
3. Build simple AML pipeline using using components for training.

<img width="1113" alt="model-asset-without-approval" src="https://user-images.githubusercontent.com/3224778/163420652-073e123a-23db-48fb-9572-da31ed72a925.png">

## Policy Creation

The Stages workflow is and and business specific logic can be enforced using Azure policy. In this example, we are going to create a policy that enforces the correct order of stage transition. I.e, we move from Dev -> Test -> Production, and should not allow Dev != prod

Step 1:  Select Azure policy from portal.azure.com

<img width="1267" alt="Screenshot 2022-07-05 at 12 16 22" src="https://user-images.githubusercontent.com/3224778/177315882-8d1b82e0-8d3e-4f37-bd27-6de322ae8d54.png">

Step 2: Click on policy definition on the left, and select "+Policy definition". This will open up the policy authoring dialog. 

<img width="1647" alt="Screenshot 2022-07-05 at 12 20 19" src="https://user-images.githubusercontent.com/3224778/177316439-5cd90ecd-7ecd-4b3f-bcc0-bc61e0f9399a.png">

Please select the definition location, which would be the subscription you would like to use. Choose "existing category" and select "Machine learning".  By default, it provides a policy template. 

Here is a simple example that uses Tags as the stage property to apply policy. 

````json

{
  "mode": "All",
  "policyRule": {
    "if": {
      "allOf": [
        {
          "field": "type",
          "equals": "Microsoft.MachineLearningServices/workspaces/models/versions"
        },
        {
          "field": "Microsoft.MachineLearningServices/workspaces/models/versions/tags",
          "containsKey": "none"
        },
        {
          "allOf": [
            {
              "field": "Microsoft.MachineLearningServices/workspaces/models/versions/tags",
              "containsKey": "[parameters('StageName1')]"
            },
            {
              "field": "Microsoft.MachineLearningServices/workspaces/models/versions/tags",
              "containsKey": "[parameters('StageName4')]"
            }
          ]
        }
      ]
    },
    "then": {
      "effect": "deny"
    }
  },
  "parameters": {
    "StageName1": {
      "type": "String",
      "metadata": {
        "displayName": "Stage Name 1",
        "description": "Name of the stage, such as 'environment'"
      }
    },
    "StageName4": {
      "type": "String",
      "metadata": {
        "displayName": "Stage Name 4",
        "description": "Name of the stage, such as 'environment'"
      }
    }
  }
}


````

## Policy Assignment

Once the policy is created, the next thing to do is assign the policy to a resource.  This can be done at the subscription or resource group level. 

In this example, we are going to do it at the resource group level. 

<img width="1652" alt="Screenshot 2022-07-05 at 12 37 01" src="https://user-images.githubusercontent.com/3224778/177318950-8a103af8-bcc4-4cab-ab0c-7630d7026edf.png">


Every workspaces in the resource group will have the policy enabled. 


## Create AML Pipeline Using AML Component


````json 

$schema: https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json
type: pipeline
description: "Staging and approval, build process"

compute: azureml:cpucluster

jobs:
  build_job:
    type: command
    component: file:./components/build_cmp.yml

````


## GitHub Action for CI/CD Pipeline

The CI/CD GitHUb action pipeline is executed based on a PR.   This will build a new model, and register it in the None stage. 


### Register model stage as None

### Approval to Staging

### Register model stage as Staging

### Approval to Archive 

### Register model stage as production

### Trigger stage change event

### Deploy













