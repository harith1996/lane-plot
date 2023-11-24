export type PlotLabels = {
	xLabel: string;
	yLabel: string;
};

export type PlotOptions = {
	xDomain: [number,number] | undefined;
	yDomain: [number,number] | undefined;
};

export type PlotDataPoint = {
	x: number;
	y: number;
};

export type Plot = {
	labels: PlotLabels;
	options: PlotOptions;
	data: PlotDataPoint[];
};

export type PlotsProps = {
	plots: Plot[];
};
