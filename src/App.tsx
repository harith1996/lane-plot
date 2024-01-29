import React, { useEffect } from "react";
import "./App.css";
import Filters from "./components/Filters";
import LaNePlots from "./components/LaNePlots";
import { LineChartType, ScatterplotType } from "./types/PlotsTypes";
import DataService from "./services/dataService";
import { FILTER_LAYOUT } from "./layout/filterLayout";
import { LaNePlotFilterOptions, LaNePlotFilters } from "./types/FilterTypes";

const HOST = "http://localhost:5000";
const ds = new DataService(HOST);

function getScatterplot(shownPlot: string, data: any, attList: any) {
	const xLabel = ["diffNext", shownPlot].join("_");
	const yLabel = ["diffPrev", shownPlot].join("_");
	const idField = "unique_id";
	const plotData = ds.scatterplotifyData(
		data,
		xLabel,
		yLabel,
		idField,
		attList
	);
	return {
		labels: {
			xLabel: xLabel,
			yLabel: yLabel,
		},
		options: {
			xDomain: undefined, //compute domain from min-max
			yDomain: undefined,
		},
		data: plotData,
	};
}

function getLineChart(
	shownPlot: string,
	data: any,
	attList: any,
	linearizeBy: string
) {
	const xLabel = linearizeBy;
	const yLabel = shownPlot;
	const idField = "unique_id";
	const plotData = ds.linechartifyData(
		data,
		xLabel,
		yLabel,
		idField,
		attList
	);
	return {
		labels: {
			xLabel: xLabel,
			yLabel: yLabel,
		},
		options: {
			xDomain: undefined, //compute domain from min-max
			yDomain: undefined,
		},
		data: plotData,
	};
}

function App() {
	const [activePlots, setActivePlots] = React.useState<any[]>([]);
	const [filterMap, setFilterMap] = React.useState<LaNePlotFilters>({
		linearizeBy: "time_stamp",
		eventType: "",
		sliceBy: "",
		sliceByValue: "",
		shownPlots: [],
	});
	const [filterOptions, setFilterOptions] =
		React.useState<LaNePlotFilterOptions>({
			linearizeBy: [],
			eventType: [],
			sliceBy: [],
			sliceByValue: [],
			shownPlots: [],
		});
	useEffect(() => {
		//fetch filter options
		ds.fetchFilterOptions(filterMap).then((filterOptions) => {
			//set filter options
			setFilterOptions(filterOptions);
			const dataPromises = filterMap.shownPlots.map((shownPlot) => {
				return ds.fetchData(
					filterMap.sliceBy,
					filterMap.sliceByValue,
					shownPlot
				);
			});
			const plotPromises = Promise.all(dataPromises).then((datasets) => {
				const scatterplots = datasets.map((dataset) => {
					const reqAttributes = dataset.reqAttributes;
					const data = dataset.data;
					const shownPlot = dataset.shownPlot;
					const attList = reqAttributes.split(",");
					return getScatterplot(shownPlot, data, attList);
				});
				const linecharts = datasets.map((dataset) => {
					const reqAttributes = dataset.reqAttributes;
					const data = dataset.data;
					const shownPlot = dataset.shownPlot;
					const attList = reqAttributes.split(",");
					return getLineChart(
						shownPlot,
						data,
						attList,
						filterMap.linearizeBy
					);
				});
				return { scatterplots, linecharts };
			});
			plotPromises.then((plots) => {
				const active = plots.scatterplots.map((plot, index) => {
					return {
						scatterplot: plot,
						linechart: plots.linecharts[index],
					};
				});
				setActivePlots(active);
			});
		});

		//fetch new filter options
	}, [filterMap]);

	const onFilterChange = (filterMap: LaNePlotFilters) => {
		setFilterMap(filterMap);
	};

	return (
		<div className="App">
			<div>
				<Filters
					filterValues={filterMap}
					filterOptions={filterOptions}
					onFilterChange={onFilterChange}
				></Filters>
			</div>
			<div>
				<LaNePlots
					activePlots={activePlots}
				></LaNePlots>
			</div>
		</div>
	);
}

export default App;
