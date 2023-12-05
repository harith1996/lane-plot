import React from "react";
import { useD3 } from "../hooks/useD3";
import { ScatterplotType } from "../types/PlotsTypes";
import * as d3 from "d3";
import * as d3Hexbin from "d3-hexbin";
import Legend from "../d3/Legend";
type ScatterplotProps = {
	plot: ScatterplotType;
	selectionCallback: any;
	selectedIds: string[];
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
	const selectedIds = props.selectedIds;
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
				.rangeRound([margin.top, height - margin.bottom])
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
					.transition()
					.attr("transform", `translate(0,${yScale(0)})`)
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
				g
					.transition()
					.attr("transform", `translate(${xScale(0)},0)`)
					.call(
						d3
							.axisLeft(yScale)
							.tickValues(
								d3
									.ticks(...yTicks, height / 80)
									.filter((v) => xScale(v) !== undefined)
							)
							.tickSizeOuter(0)
					);

			const xLabel = (g: any) => {
				const x = width - margin.right;
				const y = yScale(0) - 6;
				return g
					.transition()
					.attr("class", "x-label")
					.attr("text-anchor", "end")
					.attr("x", x)
					.attr("y", y)
					.text(plot.labels.xLabel);
			};

			const yLabel = (g: any) => {
				const x = xScale(0) + 6;
				const y = margin.top;
				return g
					.transition()
					.attr("class", "y-label")
					.attr("text-anchor", "start")
					.attr("x", x)
					.attr("y", y)
					.text(plot.labels.yLabel);
			};

			svg.select(".x-axis").call(xAxis);
			svg.select(".y-axis").call(yAxis);
			svg.select(".x-label").call(xLabel);
			svg.select(".y-label").call(yLabel);

			// Append the dots or bins.
			const radius = 5;
			const hexbin = d3Hexbin
				.hexbin()
				// @ts-ignore
				.x((d) => xScale(d.x))
				// @ts-ignore
				.y((d) => yScale(d.y))
				.radius((radius * width) / (height - 1))
				.extent([
					[margin.left, margin.top],
					[width - margin.right, height - margin.bottom],
				]);

			// @ts-ignore
			let bins = hexbin(data);

			bins.forEach((b) => {
				// @ts-ignore
				let idsInBin = b.map((d) => d.id);
				const filteredArray = idsInBin.filter((value) =>
					selectedIds.includes(value)
				);
				// @ts-ignore
				b.isSelected = filteredArray.length > 0;
			});
			const colorScale = d3
				.scaleSequentialSymlog(d3.interpolateBlues)
				.domain([0, Math.max(...bins.map((b) => b.length))]);

			const plotArea = svg.select(".plot-area");
			const onBinClick = function (event: any, d: any) {
				let selection = d.map((d: any) => d.id);
				if (d.isSelected) {
					//unselect this bin
					d.isSelected = false;
					selectionCallback(
						selectedIds.filter((id) => !selection.includes(id))
					);
				} else {
					if (event.ctrlKey) {
						selection = [...selectedIds, ...selection];
					}
					selectionCallback(selection);
				}
			};
			plotArea
				.attr("stroke", "#000")
				.attr("stroke-opacity", 0.5)
				.selectAll("path")
				.data(bins)
				.join("path")
				.attr("d", hexbin.hexagon())
				.on("click", onBinClick)
				.transition()
				.duration(300)
				.attr("transform", (d) => `translate(${d.x},${d.y})`)
				.attr("fill", (d) => colorScale(d.length))
				.attr("opacity", (d: any) => {
					return d.isSelected ? 1 : 1;
				})
				.attr("stroke", (d: any) => {
					return d.isSelected ? "red" : "black";
				})
				.attr("stroke-width", (d: any) => {
					return d.isSelected ? 2 : 1;
				});

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
		[plot, selectedIds]
	);
	return (
		<div>
			<svg
				ref={ref}
				style={{
					height: 700,
					width: 700,
					marginRight: "0px",
					marginLeft: "0px",
				}}
			>
				<g className="plot-area" />
				<g className="x-axis" />
				<text className="x-label" />
				<text className="y-label" />
				<g className="y-axis" />
				<g className="colorLegend" />
			</svg>
		</div>
	);
}
