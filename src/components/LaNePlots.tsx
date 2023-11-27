import React from "react";
import Scatterplot from "./Scatterplot";
import { PlotsProps } from "../types/PlotsTypes";

export default function LaNePlots(props: PlotsProps) {
	const [selectedData, setSelectedData] = React.useState<any[]>([]);

	const onSelectionChange = (data: any) => {
		console.log(data);
	};
	return (
		<div>

			{props.plots.map((plot) => {
				return (
					<div>
						<Scatterplot plot={plot} selectionCallback={onSelectionChange} ></Scatterplot>
					</div>
				);
			})}
		</div>
	);
}
