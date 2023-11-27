import React from "react";
import SingleSelect from "./SingleSelect";
import MultiSelect from "./MultiSelect";

export default function Filters({ onFilterChange }: any) {
	//Filter states
	const [linearizeBy, setLinearizeBy] = React.useState<string>("");
	const [eventType, setEventType] = React.useState<string>("");
	const [sliceBy, setSliceBy] = React.useState<string>("page_id");
	const [sliceByValue, setSliceByValue] = React.useState<any>("74804817");
	const [shownPlots, setShownPlots] = React.useState<string[]>([]);

	const [eventTypeOptions, setEventTypeOptions] = React.useState<string[]>(
		[]
	);
	const [sliceByOptions, setSliceByOptions] = React.useState<string[]>([
		"page_id",
		"event_user_id",
	]); //TODO: fetch from server
	const [sliceByValueOptions, setSliceByValueOptions] = React.useState<any[]>(
		[
			"74804817",
			"1952670",
			"74199488",
			"70308452",
			"68401269",
		]
	);
	const [shownPlotsOptions, setShownPlotsOptions] = React.useState<string[]>(
		[]
	);
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
		onFilterChange({ sliceBy: value, sliceByValue: defaultSliceByValue });
	};
	const onSliceByValueChange = (value: any) => {
		setSliceByValue(value);
		onFilterChange({ sliceBy: sliceBy, sliceByValue: value });
		//fetch new data
	};
	const onShownPlotsChange = (value: string[]) => {
		setShownPlots(value);
		//fetch new data
	};

	return (
		<div>
			<div>
				Filters
				<SingleSelect
					options={sliceByOptions}
					onChange={onSliceByChange}
					label={sliceByLabel}
					selectedValue={sliceBy}
				></SingleSelect>
				<SingleSelect
					options={sliceByValueOptions}
					onChange={onSliceByValueChange}
					label={sliceBy}
					selectedValue={sliceByValue}
				></SingleSelect>
			</div>
			<div>
				<MultiSelect></MultiSelect>
			</div>
		</div>
	);
}
