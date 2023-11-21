import React from "react";
import { useD3 } from "../hooks/useD3";
import { Plot } from "../types/PlotsTypes";
import * as d3 from "d3";
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
			const margin = { top: 20, right: 30, bottom: 30, left: 40 };

			const x = d3
				.scaleLinear()
				.domain(plot.options.xDomain)
				.rangeRound([margin.left, width - margin.right]);

			const y = d3
				.scaleLinear()
				.domain(plot.options.yDomain)
				.rangeRound([height - margin.bottom, margin.top]);

			const xTicks: [number, number] = d3.extent(x.domain()) as [
				number,
				number
			];

			const yTicks: [number, number] = d3.extent(y.domain()) as [
				number,
				number
			];

			const xAxis = (g: any) =>
				g
					.attr("transform", `translate(0,${height - margin.bottom})`)
					.call(
						d3
							.axisBottom(x)
							.tickValues(
								d3
									.ticks(...xTicks, width / 40)
									.filter((v) => x(v) !== undefined)
							)
							.tickSizeOuter(0)
					);

			const yAxis = (g: any) =>
				g.attr("transform", `translate(${margin.left},0)`).call(
					d3
						.axisLeft(y)
						.tickValues(
							d3
								.ticks(...yTicks, height / 40)
								.filter((v) => x(v) !== undefined)
						)
						.tickSizeOuter(0)
				);

			svg.select(".x-axis").call(xAxis);
			svg.select(".y-axis").call(yAxis);

			// Append the dots.
			const plotArea = svg.select(".plot-area");
			const dot = plotArea
					.attr("stroke", "steelblue")
					.attr("stroke-width", 0)
				.selectAll("circle")
				.data(data)
				.join("circle")
					.attr("transform", (d) => `translate(${x(d.x)},${y(d.y)})`)
					.attr("r", 7)
					.attr("opacity", 0.3);
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
