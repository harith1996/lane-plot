import React from "react";
import SingleSelect from "./SingleSelect";
import MultiSelect from "./MultiSelect";
import { LaNePlotFilters } from "../types/FilterTypes";

export default function Filters({ selectedFilters, onFilterChange }: { selectedFilters: LaNePlotFilters, onFilterChange: any}) {
	//Filter states
	const [linearizeBy, setLinearizeBy] = React.useState<string>(selectedFilters.linearizeBy);
	const [eventType, setEventType] = React.useState<string>(selectedFilters.eventType);
	const [sliceBy, setSliceBy] = React.useState<string>(selectedFilters.sliceBy);
	const [sliceByValue, setSliceByValue] = React.useState<any>(selectedFilters.sliceByValue);
	const [shownPlots, setShownPlots] = React.useState<string[]>(selectedFilters.shownPlots);

	const [eventTypeOptions, setEventTypeOptions] = React.useState<string[]>(
		[]
	);
	const [sliceByOptions, setSliceByOptions] = React.useState<string[]>([
		"page_id",
		"event_user_id",
	]); //TODO: fetch from server
	const [sliceByValueOptions, setSliceByValueOptions] = React.useState<any[]>(
		["74804817", "1952670", "74199488", "70308452", "68401269"]
	);
	const [shownPlotsOptions, setShownPlotsOptions] = React.useState<string[]>([
		"revision_text_bytes",
		"event_timestamp",
	]);
	const [linearizeByOptions, setLinearizeByOptions] = React.useState<
		string[]
	>([]);
	const linearizeLabel = "Linearize By";
	const sliceByLabel = "Slice By";

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
		let defaultSliceByValue = "";
		switch (value) {
			case "page_id":
				setSliceByValueOptions([
					"74804817",
					"1952670",
					"74199488",
					"70308452",
					"68401269",
				]); //TODO: fetch from server
				defaultSliceByValue = "74804817";
				break;
			case "event_user_id":
				setSliceByValueOptions([
					"3455093",
					"7903804",
					"7852030",
					"2842084",
					"15996738",
				]); //TODO: fetch from server
				defaultSliceByValue = "3455093";
				break;
			//fetch new data
		}
		setSliceByValue(defaultSliceByValue);
		onFilterChange({
			sliceBy: value,
			sliceByValue: defaultSliceByValue,
			shownPlots: shownPlots,
		});
	};
	const onSliceByValueChange = (value: any) => {
		setSliceByValue(value);
		onFilterChange({
			sliceBy: sliceBy,
			sliceByValue: value,
			shownPlots: shownPlots,
		});
		//fetch new data
	};
	const onShownPlotsChange = (value: string[]) => {
		setShownPlots(value);
		
		onFilterChange({
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
