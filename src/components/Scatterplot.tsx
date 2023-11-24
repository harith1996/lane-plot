import React from "react";
import { useD3 } from "../hooks/useD3";
import { Plot } from "../types/PlotsTypes";
import * as d3 from "d3";
import * as d3Hexbin from "d3-hexbin";
import Legend from "../d3/Legend";
type ScatterplotProps = {
	plot: Plot;
	selectionCallback: any;
};

function getDomains(
	data: any[],
	xDomain: [number, number] | undefined,
	yDomain: [number, number] | undefined
) {
	let xDomainNew =
		xDomain || (d3.extent(data, (d) => d.x) as [number, number]);
	let yDomainNew =
		yDomain || (d3.extent(data, (d) => d.y) as [number, number]);
	if (xDomainNew[0] > 0) {
		xDomainNew[0] = 0;
	}
	if (yDomainNew[0] > 0) {
		yDomainNew[0] = 0;
	}
	if (xDomainNew[1] < 0) {
		xDomainNew[1] = 0;
	}
	if (yDomainNew[1] < 0) {
		yDomainNew[1] = 0;
	}

	//add padding to domain
	const xDomainPadding = (xDomainNew[1] - xDomainNew[0]) * 0.1;
	const yDomainPadding = (yDomainNew[1] - yDomainNew[0]) * 0.1;
	xDomainNew[0] -= xDomainPadding;
	xDomainNew[1] += xDomainPadding;
	yDomainNew[0] -= yDomainPadding;
	yDomainNew[1] += yDomainPadding;

	return [xDomainNew, yDomainNew];
}

export default function Scatterplot(props: ScatterplotProps) {
	const plot = props.plot;
	const selectionCallback = props.selectionCallback;
	const data = plot.data;
	const ref = useD3(
		(svg) => {
			const height = 700;
			const width = 700;
			const margin = { top: 20, right: 30, bottom: 80, left: 60 };

			const [xDomain, yDomain] = getDomains(
				data,
				plot.options.xDomain,
				plot.options.yDomain
			);

			const xScale = d3
				.scaleSymlog()
				.domain(xDomain)
				.rangeRound([margin.left, width - margin.right])
				.clamp(true);

			const yScale = d3
				.scaleSymlog()
				.domain(yDomain)
				.rangeRound([height - margin.bottom, margin.top])
				.clamp(true);

			const xTicks: [number, number] = d3.extent(xScale.domain()) as [
				number,
				number
			];

			const yTicks: [number, number] = d3.extent(yScale.domain()) as [
				number,
				number
			];

			const xAxis = (g: any) =>
				g.attr("transform", `translate(0,${yScale(0)})`).call(
					d3
						.axisBottom(xScale)
						.tickValues(
							d3
								.ticks(...xTicks, width / 80)
								.filter((v) => xScale(v) !== undefined)
						)
						.tickSizeOuter(0)
				);

			const yAxis = (g: any) =>
				g.attr("transform", `translate(${xScale(0)},0)`).call(
					d3
						.axisLeft(yScale)
						.tickValues(
							d3
								.ticks(...yTicks, height / 80)
								.filter((v) => xScale(v) !== undefined)
						)
						.tickSizeOuter(0)
				);

			svg.select(".x-axis").call(xAxis);
			svg.select(".y-axis").call(yAxis);

			// Append the dots.
			const radius = 5;
			const hexbin = d3Hexbin
				.hexbin()
				.x((d) => xScale(d[0]))
				.y((d) => yScale(d[1]))
				.radius((radius * width) / (height - 1))
				.extent([
					[margin.left, margin.top],
					[width - margin.right, height - margin.bottom],
				]);
			let bins = hexbin(data.map((d) => [d.x, d.y]));
			const colorScale = d3
				.scaleSequentialSymlog(d3.interpolateBlues)
				.domain([0, Math.max(...bins.map((b) => b.length))]);

			const plotArea = svg.select(".plot-area");
			plotArea
				.attr("stroke", "#000")
				.attr("stroke-opacity", 0.5)
				.selectAll("path")
				.data(bins)
				.join("path")
				.attr("d", hexbin.hexagon())
				.attr("transform", (d) => `translate(${d.x},${d.y})`)
				.attr("fill", (d) => colorScale(d.length));

			// append color legend
			const legend = Legend(colorScale, {
				title: "Number of points",
			});
			svg.select(".colorLegend")
				.html(legend?.innerHTML as string)
				.attr(
					"transform",
					`translate(${margin.left},${height - margin.bottom + 30})`
				);
			/*************** BINNED SCATTERPLOT */

			/*************** SCATTERPLOT
			const dot = plotArea
					.attr("stroke", "steelblue")
					.attr("stroke-width", 0)
				.selectAll("circle")
				.data(data)
				.join("circle")
					.attr("transform", (d) => `translate(${xScale(d.x)},${yScale(d.y)})`)
					.attr("r", 7)
					.attr("opacity", 0.3);
			****************/

			// svg.call(
			// 	d3.brush().on("start brush end", ({ selection }) => {
			// 		let value: any[] = [];
			// 		if (selection) {
			// 			const [[x0, y0], [x1, y1]] = selection;
			// 			value = dot
			// 				.style("stroke", "gray")
			// 				.filter(
			// 					(d) =>
			// 						x0 <= x(d.x) &&
			// 						x(d.x) < x1 &&
			// 						y0 <= y(d.y) &&
			// 						y(d.y) < y1
			// 				)
			// 				.style("stroke", "steelblue")
			// 				.data();
			// 		} else {
			// 			dot.style("stroke", "steelblue");
			// 		}

			// 		// Inform downstream cells that the selection has changed.
			// 		svg.property("value", value).dispatch("input");
			// 		selectionCallback(value);
			// 	}) as any
			// );
		},
		[plot]
	);
	return (
		<div>
			<svg
				ref={ref}
				style={{
					height: 1000,
					width: "100%",
					marginRight: "0px",
					marginLeft: "0px",
				}}
			>
				<g className="plot-area" />
				<g className="x-axis" />
				<g className="y-axis" />
				<g className="colorLegend" />
			</svg>
		</div>
	);
}
