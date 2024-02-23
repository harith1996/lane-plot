import CustomRadioGroup from "./CustomRadioGroup";
import { useState } from "react";

type VisControlsProps = {
	plotType: string;
	plotOptions: string[];
    onPlotTypeChange: (plotType: string) => void;
};

export default function VisControls(props: VisControlsProps) {
	return (
		<div>
			<CustomRadioGroup
				label={"Scatterplot type"}
				options={props.plotOptions}
				value={props.plotType}
				onChange={props.onPlotTypeChange}
			/>
		</div>
	);
}
