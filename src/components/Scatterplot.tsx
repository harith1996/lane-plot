import React from "react";
import { useD3 } from "../hooks/useD3";
import { Plot } from "../types/PlotsTypes";
import * as d3 from "d3";
import * as d3Hexbin from "d3-hexbin";
type ScatterplotProps = {
	plot: Plot;
	selectionCallback: any;
};

export default function Scatterplot(props: ScatterplotProps) {
	const plot = props.plot;
	const selectionCallback = props.selectionCallback;
	const data = plot.data;
	const ref = useD3(
		(svg) => {
			const height = 500;
			const width = 500;
			const margin = { top: 20, right: 30, bottom: 30, left: 60 };

			const xScale = d3
				.scaleSymlog()
				.domain(
					plot.options.xDomain ||
						(d3.extent(data, (d) => d.x) as [number, number])
				)
				.rangeRound([margin.left, width - margin.right])
				.clamp(true);

			const yScale = d3
				.scaleSymlog()
				.domain(
					plot.options.yDomain ||
						(d3.extent(data, (d) => d.y) as [number, number])
				)
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
				g
					.attr("transform", `translate(0,${height - margin.bottom})`)
					.call(
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
				g.attr("transform", `translate(${margin.left},0)`).call(
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
					height: 500,
					width: "100%",
					marginRight: "0px",
					marginLeft: "0px",
				}}
			>
				<g className="plot-area" />
				<g className="x-axis" />
				<g className="y-axis" />
			</svg>
		</div>
	);
}
