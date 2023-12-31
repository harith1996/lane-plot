export type PlotLabels = {
	xLabel: string;
	yLabel: string;
};

export type PlotOptions = {
	xDomain: [number,number] | undefined;
	yDomain: [number,number] | undefined;
};

export type ScatterplotDataPoint = {
	x: number;
	y: number;
	id: string;
};

export type LineChartDataPoint = {
	date: string;
	value: number;
	id: string; 
}

export type ScatterplotType = {
	labels: PlotLabels;
	options: PlotOptions;
	data: ScatterplotDataPoint[];
};

export type LineChartType = {
	labels: PlotLabels;
	options: PlotOptions;
	data: LineChartDataPoint[];
};

export type PlotsProps = {
	activePlots: {
		scatterplot: ScatterplotType;
		linechart: LineChartType;
	}[];
};
