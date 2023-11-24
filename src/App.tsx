import React, { useEffect } from "react";
import "./App.css";
import Filters from "./components/Filters";
import Plots from "./components/Plots";
import { Plot } from "./types/PlotsTypes";
import DataService from "./services/dataService";


function App() {
	const [activePlots, setActivePlots] = React.useState<Plot[]>([]);
	const ds = new DataService("http://localhost:5000");
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
						xLabel: "diffNext_revision_bytes",
						yLabel: "diffPrev_revision_bytes",
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
	return (
			<div className="App">
				<div>
					<Filters></Filters>
				</div>
				<div>
					<Plots plots={activePlots}></Plots>
				</div>
			</div>
	);
}

export default App;
