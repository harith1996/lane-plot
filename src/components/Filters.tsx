import React from 'react'
import SingleSelect from './SingleSelect';
import MultiSelect from './MultiSelect';

export default function Filters() {
     //Filter states
  const [linearizeBy, setLinearizeBy] = React.useState<string>("");
  const [eventType, setEventType] = React.useState<string>("");
  const [sliceBy, setSliceBy] = React.useState<string>("");
  const [sliceByValue, setSliceByValue] = React.useState<any>("");
  const [shownPlots, setShownPlots] = React.useState<string[]>([]);

  const [eventTypeOptions, setEventTypeOptions] = React.useState<string[]>([]);
  const [sliceByOptions, setSliceByOptions] = React.useState<string[]>([]);
  const [sliceByValueOptions, setSliceByValueOptions] = React.useState<any[]>([]);
  const [shownPlotsOptions, setShownPlotsOptions] = React.useState<string[]>([]);
  const [linearizeByOptions, setLinearizeByOptions] = React.useState<string[]>([]);
  const linearizeLabel = "Linearize By";

  const onLinearizeByChange = (value: string) => {
    setLinearizeBy(value);
    //fetch new data
  };
  const onEventTypeChange = (value: string) => {
    setEventType(value);
    //fetch new data
  };
  const onSliceByChange = (value: string) => {
    setSliceBy(value);
    //fetch new data
  }
  const onSliceByValueChange = (value: any) => {
    setSliceByValue(value);
    //fetch new data
  }
  const onShownPlotsChange = (value: string[]) => {
    setShownPlots(value);
    //fetch new data
  }

  return (
    <div>
              <div>
        Filters
      <SingleSelect options={linearizeByOptions} onChange={onLinearizeByChange} label={linearizeLabel} selectedValue={linearizeBy}></SingleSelect>
      </div>
      <div>
        <MultiSelect></MultiSelect>
      </div>
    </div>
  )
}
