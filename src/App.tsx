import React, { useEffect } from "react";
import "./App.css";
import Filters from "./components/Filters";
import LaNePlots from "./components/LaNePlots";
import DataService from "./services/dataService";
import { LaNePlotFilterOptions, LaNePlotFilters } from "./types/FilterTypes";
import helper_img from "./static/images/quadrant_labels.drawio.png";
import VisControls from "./components/VisControls";

const HOST = "http://localhost:5000";
const ds = new DataService(HOST);

function getScatterplot(shownPlot: string, data: any, attList: any, isBinned: boolean, idField: string = "rev_id") {
	const xLabel = ["diffNext", shownPlot].join("_");
	const yLabel = ["diffLast", shownPlot].join("_");
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
		isBinned: isBinned,
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
	const [plotType, setPlotType] = React.useState<string>("Normal");
	const [activePlots, setActivePlots] = React.useState<any[]>([]);
	const [filterMap, setFilterMap] = React.useState<LaNePlotFilters>({
		linearizeBy: "timestamp",
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
					"timestamp",
					[
						"page_name",
						"comment",
						"rev_id",
						"is_reverted",
						"tags"
					]
				);
			});
			const plotPromises = Promise.all(dataPromises).then((datasets) => {
				const scatterplots = datasets.map((dataset) => {
					const reqAttributes = dataset.reqAttributes;
					const attList = reqAttributes.split(",");
					const data = dataset.data;
					const shownPlot = dataset.shownPlot;
					const idField = "rev_id"; //@TODO: add filter option to choose event.
					return getScatterplot(shownPlot, data, attList, plotType === "Binned", idField);
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
	}, [filterMap, plotType]);

	const onFilterChange = (filterMap: LaNePlotFilters) => {
		setFilterMap(filterMap);
	};

	const scatterplotInspectCallback = (currId: string) => {
		const linearizeBy = filterMap.linearizeBy;
		const sliceByField = filterMap.sliceBy;
		const sliceByValue = filterMap.sliceByValue;
		const eventIdField = "rev_id";
		ds.fetchAdjacentEvents(linearizeBy, sliceByField, sliceByValue, eventIdField, currId).then((adjacentEvents) => {
			// open diff url in new tab
			window.open(`https://en.wikipedia.org/w/index.php?diff=${adjacentEvents.currId}&oldid=${adjacentEvents.nextId}`, "_blank");
		});
	}

	return (
		<div className="App">
			<div className="controls">
				<Filters
					filterValues={filterMap}
					filterOptions={filterOptions}
					onFilterChange={onFilterChange}
					getHelperText={ds.fetchHumanReadableEntityName.bind(ds)}
				></Filters>
				<VisControls
					plotType={plotType}
					plotOptions={["Normal", "Binned"]}
					onPlotTypeChange={setPlotType}
				></VisControls>
			</div>
			<div>
				<LaNePlots activePlots={activePlots} scatterplotInspectCallback={scatterplotInspectCallback}></LaNePlots>
			</div>

			<div style={{ color: "red" }}>red = reversions</div>
			<div>
				<img
					src={helper_img}
					alt="quadrant_labels"
					width="900"
					height="400"
				/>
			</div>
		</div>
	);
}

export default App;
