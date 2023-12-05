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
			{props.scatterplots.map((plot, index) => {
				return (
					<div key={index}>
						<Scatterplot
							plot={plot}
							selectionCallback={onSelectionChange}
							selectedIds={selectedData}
						></Scatterplot>
					</div>
				);
			})}
			{/* {props.linecharts.map((plot, index) => {
				return (
					<div key={index}>
						<LineChart
							plot={plot}
							selectionCallback={onSelectionChange}
							selectedIds={selectedData}
						></LineChart>
					</div>
				);
			})} */}
		</div>
	);
}
