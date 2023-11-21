import React from "react";
import Scatterplot from "./Scatterplot";
import { PlotsProps } from "../types/PlotsTypes";

export default function Plots(props: PlotsProps) {
	const [selectedData, setSelectedData] = React.useState<any[]>([]);

	return (
		<div>
			Plots
			{props.plots.map((plot) => {
				return (
					<div>
						{JSON.stringify(plot.labels)}
						<Scatterplot {...plot}></Scatterplot>
					</div>
				);
			})}
		</div>
	);
}
