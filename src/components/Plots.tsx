import React from "react";
import Scatterplot from "./Scatterplot";
import { PlotsProps } from "../types/PlotsTypes";

export default function Plots(props: PlotsProps) {
	const [selectedData, setSelectedData] = React.useState<any[]>([]);

	const onSelectionChange = (data: any) => {
		console.log(data);
	};
	return (
		<div>
			Plots
			{props.plots.map((plot) => {
				return (
					<div>
						{JSON.stringify(plot.labels)}
						<Scatterplot plot={plot} selectionCallback={onSelectionChange} ></Scatterplot>
					</div>
				);
			})}
		</div>
	);
}
