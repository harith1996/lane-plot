export const FILTER_LAYOUT = {
	singleSelect: [
		// linearizeBy: {
		// 	label: "Linearize By",
		// 	fetchFrom: "linearizeables",
		// },
		{
			name: "linearizeBy",
			label: "Linearize By",
			fetchOptionsFrom: "linearizeables",
			
		},
		{
			name: "eventType",
			label: "Event Type",
			fetchOptionsFrom: "eventTypes",
		},
		{
			name: "sliceBy",
			label: "Slice By",
			fetchOptionsFrom: "sliceables",
		},
		{
			name: "sliceByValue",
			label: "Slice By Value",
			fetchOptionsFrom: "sliceableValues",
		},
	],

	multiSelect: [
		{
			name: "shownPlots",
			label: "Shown Plots",
			fetchOptionsFrom: "diffableAttributes",
		},
	],
};