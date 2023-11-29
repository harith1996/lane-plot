import React, { useEffect } from "react";
import "./App.css";
import Filters from "./components/Filters";
import LaNePlots from "./components/LaNePlots";
import { Plot } from "./types/PlotsTypes";
import DataService from "./services/dataService";
import { fetchFilterOptions, FILTER_LAYOUT } from "./layout/filterLayout";
import { LaNePlotFilters } from "./types/FilterTypes";

const HOST = "http://localhost:5000";
const ds = new DataService(HOST);

function getPlot(shownPlot: string, data: any, attList: any) {
	const xLabel = ["diffNext", shownPlot].join("_");
	const yLabel = ["diffPrev", shownPlot].join("_");
	const plotData = ds.plotsifyData(data, xLabel, yLabel, attList);
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
	const [activePlots, setActivePlots] = React.useState<Plot[]>([]);
	const [filterMap, setFilterMap] = React.useState<LaNePlotFilters>({
		linearizeBy: "event_timestamp",
		eventType: "revision_create",
		sliceBy: "page_id",
		sliceByValue: "74804817",
		shownPlots: ["revision_text_bytes"],
	});
	useEffect(() => {
		//fetch new data for plot
		const dataPromises = filterMap.shownPlots.map((shownPlot) => {
			return ds.fetchData(
				filterMap.sliceBy,
				filterMap.sliceByValue,
				shownPlot
			);
		});
		const plotPromises = Promise.all(dataPromises).then((datasets) => {
			return datasets.map((dataset) => {
				const reqAttributes = dataset.reqAttributes;
				const data = dataset.data;
				const shownPlot = dataset.shownPlot;
				const attList = reqAttributes.split(",");
				return getPlot(shownPlot, data, attList);
			});
		});
		plotPromises.then((plots) => {
			setActivePlots(plots);
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
					selectedFilters={filterMap}
					onFilterChange={onFilterChange}
				></Filters>
			</div>
			<div>
				<LaNePlots plots={activePlots}></LaNePlots>
			</div>
		</div>
	);
}

export default App;
