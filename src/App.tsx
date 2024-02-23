import React, { useEffect } from "react";
import "./App.css";
import Filters from "./components/Filters";
import LaNePlots from "./components/LaNePlots";
import { LineChartType, ScatterplotType } from "./types/PlotsTypes";
import DataService from "./services/dataService";
import { FILTER_LAYOUT } from "./layout/filterLayout";
import { LaNePlotFilterOptions, LaNePlotFilters } from "./types/FilterTypes";
import helper_img from "./static/images/quadrant_labels.drawio.png";

const HOST = "http://localhost:5000";
const ds = new DataService(HOST);

function getScatterplot(shownPlot: string, data: any, attList: any) {
	const xLabel = ["diffNext", shownPlot].join("_");
	const yLabel = ["diffPrev", shownPlot].join("_");
	const idField = "unique_id";
	// const colorField = "time_till_election";
	const colorField = "is_reverted";
	const plotData = ds.scatterplotifyData(
		data,
		xLabel,
		yLabel,
		idField,
		colorField,
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
					shownPlot,
					"time_stamp",
					["article_title", "comment", "rev_id", "is_reverted", "time_till_election"]
				);
			});
			const plotPromises = Promise.all(dataPromises).then((datasets) => {
				const scatterplots = datasets.map((dataset) => {
					const reqAttributes = dataset.reqAttributes;
					const attList = reqAttributes.split(",");
					const data = dataset.data;
					const shownPlot = dataset.shownPlot;
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
					getHelperText={ds.fetchHumanReadableEntityName.bind(ds)}
				></Filters>
			</div>
			<div>
				<LaNePlots activePlots={activePlots}></LaNePlots>
			</div>
			
			<div style={{"color" : "red"}}>red = reversions</div>
			<div>
				<img src={helper_img} alt="quadrant_labels" width="900" height="400" />
			</div>
			
		</div>
	);
}

export default App;
