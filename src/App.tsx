import React, { useEffect } from "react";
import "./App.css";
import Filters from "./components/Filters";
import LaNePlots from "./components/LaNePlots";
import { Plot } from "./types/PlotsTypes";
import DataService from "./services/dataService";
import { fetchFilterOptions, FILTER_LAYOUT } from "./layout/filterLayout";
import { LaNePlotFilters } from "./types/FilterTypes";

const ds = new DataService("http://localhost:5000");

function getPlot(filters: LaNePlotFilters, data: any) {
	const xLabel = ["diffNext", filters.shownPlots[0]].join("_");
	const yLabel = ["diffPrev", filters.shownPlots[0]].join("_");
	const plotData = ds.plotsifyData(data, xLabel, yLabel);

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
		ds.fetchData(filterMap.sliceBy, filterMap.sliceByValue).then((data) => {
			console.log(data);
			setActivePlots([getPlot(filterMap, data)]);
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
