import React, { useEffect } from "react";
import "./App.css";
import Filters from "./components/Filters";
import LaNePlots from "./components/LaNePlots";
import { Plot } from "./types/PlotsTypes";
import DataService from "./services/dataService";

const ds = new DataService("http://localhost:5000");
function App() {
	const [activePlots, setActivePlots] = React.useState<Plot[]>([]);
	useEffect(() => {
		ds.fetchData().then((data) => {
			console.log(data);
			//preprocess data before sending to plots
			const plotData = ds.plotsifyData(
				data,
				"diffNext_revision_text_bytes",
				"diffPrev_revision_text_bytes"
			);

			setActivePlots([
				{
					labels: {
						xLabel: "diffNext_revision_text_bytes",
						yLabel: "diffPrev_revision_text_bytes",
					},
					options: {
						xDomain: undefined, //compute domain from min-max
						yDomain: undefined,
					},
					data: plotData,
				},
			]);
		});
	}, []);
	const onFilterChange = (filterChange: any) => {
		//fetch new data
		ds.fetchData(filterChange.sliceBy, filterChange.sliceByValue).then(
			(data) => {
				console.log(data);
				//preprocess data before sending to plots
				const plotData = ds.plotsifyData(
					data,
					"diffNext_revision_text_bytes",
					"diffPrev_revision_text_bytes"
				);

				setActivePlots([
					{
						labels: {
							xLabel: "diffNext_revision_text_bytes",
							yLabel: "diffPrev_revision_text_bytes",
						},
						options: {
							xDomain: undefined, //compute domain from min-max
							yDomain: undefined,
						},
						data: plotData,
					},
				]);
			}
		);
	};
	return (
		<div className="App">
			<div>
				<Filters onFilterChange={onFilterChange}></Filters>
			</div>
			<div>
				<LaNePlots plots={activePlots}></LaNePlots>
			</div>
		</div>
	);
}

export default App;
