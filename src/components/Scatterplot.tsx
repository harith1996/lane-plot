import React from "react";
import { useD3 } from "../hooks/useD3";
import { Plot } from "../types/PlotsTypes";
import * as d3 from "d3";

export default function Scatterplot(plot: Plot) {
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
			const dot = svg
				.select(".plot-area")
				.attr("stroke", "steelblue")
				.attr("stroke-width", 0)
				.selectAll("circle")
				.data(data)
				.join("circle")
				.attr("transform", (d) => `translate(${x(d.x)},${y(d.y)})`)
				.attr("r", 7)
				.attr("opacity", 0.3);
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
