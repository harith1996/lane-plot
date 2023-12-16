import DataService from "../services/dataService";

type Filter = {
	name: string;
	label: string;
	type: string;
	fetchOptionsFrom: string;
	options: any;
};
export const FILTER_LAYOUT: Filter[] = [
	// linearizeBy: {
	// 	label: "Linearize By",
	// 	fetchFrom: "linearizeables",
	// },
	{
		name: "linearizeBy",
		label: "Linearize By",
		type: "singleSelect",
		fetchOptionsFrom: "linearizeables",
		options: [],
	},
	{
		name: "eventType",
		label: "Event Type",
		type: "singleSelect",
		fetchOptionsFrom: "eventTypes",
		options: [],
	},
	{
		name: "sliceBy",
		label: "Slice By",
		type: "singleSelect",
		fetchOptionsFrom: "sliceables",
		options: [],
	},
	{
		name: "sliceByValue",
		label: "Slice By Value",
		type: "singleSelect",
		fetchOptionsFrom: "sliceableValues",
		options: [],
	},
	{
		name: "shownPlots",
		label: "Shown Plots",
		type: "multiSelect",
		fetchOptionsFrom: "diffableAttributes",
		options: [],
	},
];
