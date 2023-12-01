import React, { useEffect } from "react";
import SingleSelect from "./SingleSelect";
import MultiSelect from "./MultiSelect";
import { LaNePlotFilterOptions, LaNePlotFilters } from "../types/FilterTypes";

export default function Filters({
	filterValues,
	filterOptions,
	onFilterChange,
}: {
	filterValues: LaNePlotFilters;
	filterOptions: LaNePlotFilterOptions;
	onFilterChange: any;
}) {
	//Filter states
	const [linearizeBy, setLinearizeBy] = React.useState<string>(
		filterValues.linearizeBy
	);
	const [eventType, setEventType] = React.useState<string>(
		filterValues.eventType
	);
	const [sliceBy, setSliceBy] = React.useState<string>(filterValues.sliceBy);
	const [sliceByValue, setSliceByValue] = React.useState<any>(
		filterValues.sliceByValue
	);
	const [shownPlots, setShownPlots] = React.useState<string[]>(
		filterValues.shownPlots
	);

	const [eventTypeOptions, setEventTypeOptions] = React.useState<string[]>(
		[]
	);
	const [sliceByOptions, setSliceByOptions] = React.useState<string[]>([]); //TODO: fetch from server
	const [sliceByValueOptions, setSliceByValueOptions] = React.useState<any[]>(
		[]
	);
	const [shownPlotsOptions, setShownPlotsOptions] = React.useState<string[]>(
		[]
	);
	const [linearizeByOptions, setLinearizeByOptions] = React.useState<
		string[]
	>([]);
	const linearizeLabel = "Linearize By";
	const sliceByLabel = "Slice By";

	useEffect(() => {
		//set all options
		setEventTypeOptions([...filterOptions.eventType]);
		setSliceByOptions([...filterOptions.sliceBy]);
		setSliceByValueOptions([...filterOptions.sliceByValue]);
		setShownPlotsOptions([...filterOptions.shownPlots]);
		setLinearizeByOptions([...filterOptions.linearizeBy]);
	}, [filterOptions]);

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
		onFilterChange({
			linearizeBy: linearizeBy,
			eventType: eventType,
			sliceBy: value,
			sliceByValue: sliceByValue,
			shownPlots: shownPlots,
		});
	};
	const onSliceByValueChange = (value: any) => {
		setSliceByValue(value);
		onFilterChange({
			linearizeBy: linearizeBy,
			eventType: eventType,
			sliceBy: sliceBy,
			sliceByValue: value,
			shownPlots: shownPlots,
		});
		//fetch new data
	};
	const onShownPlotsChange = (value: string[]) => {
		setShownPlots(value);
		onFilterChange({
			linearizeBy: linearizeBy,
			eventType: eventType,
			sliceBy: sliceBy,
			sliceByValue: sliceByValue,
			shownPlots: value,
		});
	};

	return (
		<div>
			<div className="filter-group">
				<SingleSelect
					label={sliceByLabel}
					options={sliceByOptions}
					preselected={sliceBy}
					onChange={onSliceByChange}
				></SingleSelect>
				<SingleSelect
					label={sliceBy}
					options={sliceByValueOptions}
					preselected={sliceByValue}
					onChange={onSliceByValueChange}
				></SingleSelect>
			</div>
			<div className="filter-group">
				<MultiSelect
					label={"Shown Plots"}
					options={shownPlotsOptions}
					preselected={shownPlots}
					onChange={onShownPlotsChange}
				></MultiSelect>
			</div>
		</div>
	);
}
