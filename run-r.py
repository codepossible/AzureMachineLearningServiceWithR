## run-r.py 
#
# References:
#    https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/manage-azureml-service/authentication-in-azureml/authentication-in-azureml.ipynb
#    https://docs.microsoft.com/en-us/python/api/azureml-pipeline-steps/azureml.pipeline.steps.estimator_step.estimatorstep?view=azure-ml-py
#
#
##

from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.workspace import Workspace

from azureml.core import Datastore
from azureml.train.estimator import Estimator
from azureml.pipeline.steps import EstimatorStep
from azureml.pipeline.core import PipelineParameter
from azureml.core.container_registry import ContainerRegistry

from azureml.pipeline.core import (
    Pipeline as AmlPipeline,
    PipelineRun as AmlPipelineRun,
    StepSequence as AmlStepSequence,
    PublishedPipeline as AmlPublishedPipeline
)

from dotenv import load_dotenv
import os


load_dotenv()


# Azure Subscription related information
azure_tentant_id=os.environ.get('AZURE_TENTANT_ID')
azure_subscription_id=os.environ.get('AZURE_SUBSCRIPTION_ID')
azure_app_id=os.environ.get('AZURE_APP_ID')
azure_app_secret=os.environ.get('AZURE_APP_SECRET')

# Azure Machine Learning Service related information
azure_resource_group='rg-aml-r-workloads'
aml_workspace_name='mlwks-r-workloads'
aml_experiment_name='experimenthellor'
aml_compute_target='defaultcompute'


# Azure Container Registry related information
acr_details = ContainerRegistry()
acr_details.address = os.environ.get('ACR_ADDRESS')
acr_details.username = os.environ.get('ACR_USERNAME')
acr_details.password = os.environ.get('ACR_PASSWORD')
acr_image = 'aml-r'

# R Script related information
r_script='hello.r'


#   1. Authenticate with Azure ML Service
auth = ServicePrincipalAuthentication(
            tenant_id=azure_tentant_id, 
            service_principal_id=azure_app_id, 
            service_principal_password=azure_app_secret)

aml_workspace = Workspace.get(
                    name=aml_workspace_name,
                    auth=auth,
                    subscription_id=azure_subscription_id,
                    resource_group=azure_resource_group)

if (aml_workspace):
    print(f'Connected to AML Workspace {aml_workspace._workspace_name}')
else:
    print(f'ERROR: Not connected to AML Workspace {aml_workspace_name}')
    exit(-1)

bootstrap_args = [r_script]
    
estimator = Estimator(source_directory='src',
                        entry_script='bootstrapper.py',
                        compute_target=aml_compute_target,
                        custom_docker_image=acr_image,
                        image_registry_details=acr_details,
                        user_managed=True)

inputs = []

step = EstimatorStep(
    name='execute-r',
    estimator=estimator,
    estimator_entry_script_arguments=bootstrap_args,
    inputs=inputs,
    outputs=None,
    compute_target=aml_compute_target,
    allow_reuse=False)

aml_pipeline = AmlPipeline(
                workspace=aml_workspace, 
                steps=AmlStepSequence([step]), 
                description='Run R Workloads')
    
published_pipeline = aml_pipeline.publish(
                description='Execute R Workload',
                name='pipeline-r')

    
aml_run = published_pipeline.submit(workspace=aml_workspace, 
                                    experiment_name=aml_experiment_name)

if (aml_run):
    print(f"Pipeline run started under {aml_experiment_name} with id: {aml_run}")
else:
    print(f'Failed to run {aml_experiment_name}')



