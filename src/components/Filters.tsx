import React, { useEffect } from "react";
import SingleSelect from "./SingleSelect";
import MultiSelect from "./MultiSelect";
import { LaNePlotFilterOptions, LaNePlotFilters } from "../types/FilterTypes";

class Filter {
	constructor(
		public label: string,
		public type: string,
		public endpoint: string,
		public dependsOn: Filter | null = null,
		public value: string,
		public options: string[],
		public onChange: any,
		public fetchOptions: () => Promise<string[]>
	) {
		this.label = label;
		this.type = type;
		this.endpoint = endpoint;
		this.dependsOn = dependsOn;
		this.value = "";
		this.options = [];
		this.onChange = () => {};
		this.fetchOptions = fetchOptions;
	}

	initialize() {
		//fetch options from endpoint
		//set options
		this.fetchOptions().then((options) => {
			this.options = options;
			this.value = options.length > 0 ? this.options[0] : "";
		});
	}
}

export default function Filters({
	filterValues,
	filterOptions,
	onFilterChange,
	getHelperText: fetchHelperText,
}: {
	filterValues: LaNePlotFilters;
	filterOptions: LaNePlotFilterOptions;
	onFilterChange: any;
	getHelperText: (filter: string, value: string) => Promise<any>;
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
	const [sliceByValueHelperText, setSliceByValueHelperText] =
		React.useState<string>("");
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
		fetchHelperText(sliceBy, value).then((helperText) => {
			setSliceByValueHelperText(helperText); //fetch new data
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
					selectedValue={sliceBy}
					onChange={onSliceByChange}
				></SingleSelect>
				<SingleSelect
					label={sliceBy}
					options={sliceByValueOptions}
					selectedValue={sliceByValue}
					onChange={onSliceByValueChange}
					helperText={sliceByValueHelperText}
				></SingleSelect>
				<span>slice by value helper text</span>
				<div className="filter-details">
					<></>
				</div>
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
