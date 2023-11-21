import React, { useEffect } from "react";
import "./App.css";
import Filters from "./components/Filters";
import Plots from "./components/Plots";
import { Plot } from "./types/PlotsTypes";

function App() {
	const [activePlots, setActivePlots] = React.useState<Plot[]>([]);
	useEffect(() => {
		//set dummy Plot
		setActivePlots([
			{
				labels: {
					xLabel: "x",
					yLabel: "y",
				},
				options: {
					xDomain: [0, 100],
					yDomain: [0, 100],
				},
				data: [
					{
						x: 50,
						y: 50,
					},
					{
						x: 60,
						y: 60,
					},
				],
			},
		]);
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
