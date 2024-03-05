import React from "react";
import Scatterplot from "./Scatterplot";
import { PlotsProps } from "../types/PlotsTypes";
import LineChart from "./LineChart";

export default function LaNePlots(props: PlotsProps) {
	const [selectedData, setSelectedData] = React.useState<any[]>([]);

	const onSelectionChange = (data: any) => {
		setSelectedData(data);
	};
	return (
		<div className="lane-plots">
				{props.activePlots.map((activePlot, index) => {
					return (
						<div className="plot-wrapper" key={index}>
							<Scatterplot
								plot={activePlot.scatterplot}
								selectionCallback={onSelectionChange}
								selectedIds={selectedData}
								inspectCallback={props.scatterplotInspectCallback}
							></Scatterplot>
							
							<LineChart
								plot={activePlot.linechart}
								selectionCallback={onSelectionChange}
								selectedIds={selectedData}
							></LineChart>
						</div>
					);
				})}
		</div>
	);
}
