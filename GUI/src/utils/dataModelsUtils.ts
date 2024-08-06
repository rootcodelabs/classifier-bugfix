import { DataModel } from "types/dataModels";

export const validateDataModel = (dataModel) => {
  const { modelName, dgName, platform, baseModels, maturity } = dataModel;
  const newErrors: any = {};

  if (!modelName.trim()) newErrors.modelName = 'Model Name is required';
  if (!dgName.trim()) newErrors.dgName = 'Dataset Group Name is required';
  if (!platform.trim()) newErrors.platform = 'Platform is required';
  if (baseModels?.length === 0)
    newErrors.baseModels = 'At least one Base Model is required';
  if (!maturity.trim()) newErrors.maturity = 'Maturity is required';

  return newErrors;
};

export const customFormattedArray = <T extends Record<string, any>>(data: T[], attributeName: keyof T) => {
  return data?.map((item) => ({
    label: item[attributeName],
    value: {name:item[attributeName],id:item.dgId},
  }));
};

export const getChangedAttributes = (original: DataModel, updated: DataModel): Partial<Record<keyof DataModel, string | null>> => {
  const changes: Partial<Record<keyof DataModel, string | null>> = {};

  (Object.keys(original) as (keyof DataModel)[]).forEach((key) => {
    if (original[key] !== updated[key]) {
      changes[key] = updated[key];
    } else {
      changes[key] = null;
    }
  });

  return changes;
};