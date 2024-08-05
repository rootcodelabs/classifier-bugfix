import { ChangeEvent, FC, useId, useState, useEffect } from 'react';

import './FormCheckboxes.scss';

type FormCheckboxesType = {
  label: string;
  name: string;
  hideLabel?: boolean;
  onValuesChange?: (values: Record<string, string[]>) => void;
  items: {
    label: string;
    value: string;
  }[];
  isStack?: boolean;
  error?: string;
  selectedValues?: string[]; // New prop for selected values
};

const FormCheckboxes: FC<FormCheckboxesType> = ({
  label,
  name,
  hideLabel,
  onValuesChange,
  items,
  isStack = true,
  error,
  selectedValues = [], // Default to an empty array if not provided
}) => {
  const id = useId();
  const [internalSelectedValues, setInternalSelectedValues] = useState<string[]>(selectedValues);

  useEffect(() => {
    setInternalSelectedValues(selectedValues);
  }, [selectedValues]);

  const handleValuesChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { checked, value } = e.target;

    const newValues = checked
      ? [...internalSelectedValues, value] // Add the checked value to the array
      : internalSelectedValues.filter((v: string) => v !== value); // Remove the unchecked value from the array

    setInternalSelectedValues(newValues);

    if (onValuesChange) onValuesChange({ [name]: newValues });
  };

  return (
    <div>
      <div>
        <fieldset className="checkboxes" role="group">
          {label && !hideLabel && (
            <label className="checkboxes__label">{label}</label>
          )}
          <div className={isStack ? 'checkboxes__wrapper' : 'checkboxes__row'}>
            {items.map((item, index) => (
              <div key={`${item.value}-${index}`} className="checkboxes__item">
                <input
                  type="checkbox"
                  name={name}
                  id={`${id}-${item.value}`}
                  value={item.value}
                  onChange={handleValuesChange}
                  checked={internalSelectedValues.includes(item.value)} // Manage checkbox state
                />
                <label htmlFor={`${id}-${item.value}`}>{item.label}</label>
              </div>
            ))}
          </div>
        </fieldset>
      </div>
      <div>{error && <p className="input__inline_error">{error}</p>}</div>
    </div>
  );
};

export default FormCheckboxes;
