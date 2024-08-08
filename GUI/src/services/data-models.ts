import apiDev from './api-dev';
import apiExternal from './api-external';
import apiMock from './api-mock';
import { PaginationState } from '@tanstack/react-table';
import { DatasetGroup, Operation } from 'types/datasetGroups';

export async function getDataModelsOverview(
  pageNum: number,
  modelName: string,
  majorVersion: number,
  minorVersion: number,
  platform: string,
  datasetGroup: number,
  trainingStatus: string,
  deploymentMaturity: string,
  sort: string,
  isProductionModel: boolean
) {
  const { data } = await apiDev.get('classifier/datamodel/overview', {
    params: {
      page: pageNum,
      modelName,
      majorVersion,
      minorVersion,
      platform,
      datasetGroup,
      trainingStatus,
      deploymentMaturity,
      sortType: sort,
      pageSize: 12,
      isProductionModel
    },
  });
  return data?.response;
}

export async function getFilterData() {
  const { data } = await apiDev.get('classifier/datamodel/overview/filters');
  return data?.response;
}

export async function getCreateOptions() {
  const { data } = await apiDev.get('classifier/datamodel/create/options');
  return data?.response;
}

export async function getMetadata(modelId: string | number | null) {
  const { data } = await apiDev.get('classifier/datamodel/metadata', {
    params: {
      modelId,
    },
  });
  return data?.response?.data[0];
}

export async function createDataModel(dataModel) {
  const { data } = await apiDev.post('classifier/datamodel/create', {
    ...dataModel,
  });
  return data;
}

export async function updateDataModel(dataModel) {
  const { data } = await apiDev.post('classifier/datamodel/update', {
    ...dataModel,
  });
  return data;
}

export async function deleteDataModel(modelId : number) {
  const { data } = await apiDev.post('classifier/datamodel/delete', {
    modelId
  });
  return data;
}

export async function retrainDataModel(modelId : number) {
  const { data } = await apiDev.post('classifier/datamodel/re-train', {
    modelId
  });
  return data;
}