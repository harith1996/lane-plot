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
	inspectCallback: (currId: string) => void;
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
	const inspectCallback = props.inspectCallback;
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
				// .domain(xDomain)
				.domain([-20000,20000])
				.rangeRound([margin.left, width - margin.right])
				.clamp(true);

			const yScale = d3
				.scaleSymlog()
				// .domain(yDomain.reverse())
				.domain([20000,-20000])
				.rangeRound([margin.top, height - margin.bottom])
				.clamp(true);

			const xAxis = (
				g: any,
				scale: d3.ScaleSymLog<number, number, number>,
				oppScale: d3.ScaleSymLog<number, number, number>
			) => {
				const xTicks: [number, number] = d3.extent(scale.domain()) as [
					number,
					number
				];
				g
					.transition()
					.attr("transform", `translate(0,${oppScale(0)})`)
					.call(
						d3
							.axisBottom(scale)
							.tickValues(
								d3
									.ticks(...xTicks, width / 80)
									.filter((v) => scale(v) !== undefined)
							)
							.tickSizeOuter(0)
					)
					.selectAll("*")
					.attr("opacity", 0.8)
					g.selectAll("text")
					.attr("transform", `rotate(-65) translate(-25,-7)`);
			};

			const yAxis = (
				g: any,
				scale: d3.ScaleSymLog<number, number, number>,
				oppScale: d3.ScaleSymLog<number, number, number>
			) => {
				const yTicks: [number, number] = d3.extent(scale.domain()) as [
					number,
					number
				];
				g.transition()
					.attr("transform", `translate(${oppScale(0)},0)`)
					.call(
						d3
							.axisLeft(scale)
							.tickValues(
								d3
									.ticks(...yTicks, height / 80)
									.filter((v) => scale(v) !== undefined)
							)
							.tickSizeOuter(0)
					)
					.selectAll("*")
					.attr("opacity", 0.8);
			};

			const xLabel = (
				g: any,
				scale: d3.ScaleSymLog<number, number, number>
			) => {
				const x = width - margin.right;
				const y = scale(0) - 6;
				return g
					.transition()
					.attr("class", "x-label")
					.attr("text-anchor", "end")
					.attr("x", x)
					.attr("y", y)
					.text(plot.labels.xLabel);
			};

			const yLabel = (
				g: any,
				scale: d3.ScaleSymLog<number, number, number>
			) => {
				const x = scale(0) + 6;
				const y = margin.top;
				return g
					.transition()
					.attr("class", "y-label")
					.attr("text-anchor", "start")
					.attr("x", x)
					.attr("y", y)
					.text(plot.labels.yLabel);
			};

			svg.select(".x-axis").call(xAxis, xScale, yScale);
			svg.select(".y-axis").call(yAxis, yScale, xScale);
			svg.select(".x-label").call(xLabel, yScale);
			svg.select(".y-label").call(yLabel, xScale);

			const plotArea = svg.select(".plot-area");

			// Append the dots or bins.
			plotArea.selectAll("*").remove();
			if (plot.isBinned) {
				const radius = 3;
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

				// const onBinSelect = function (event: any, d: any) {
				// 	let selection = d.map((d: any) => d.id);
				// 	if (d.isSelected) {
				// 		//unselect this bin
				// 		d.isSelected = false;
				// 		selectionCallback(
				// 			selectedIds.filter((id) => !selection.includes(id))
				// 		);
				// 	} else {
				// 		if (event.ctrlKey) {
				// 			selection = [...selectedIds, ...selection];
				// 		}
				// 		selectionCallback(selection);
				// 	}
				// };
				plotArea
					.selectAll("path")
					.data(bins)
					.join("path")
					.attr("d", hexbin.hexagon())
					// .on("mouseover", onBinSelect)
					.transition()
					.duration(300)
					.attr("transform", (d) => `translate(${d.x},${d.y})`)
					.attr("fill", (d) => colorScale(d.length))
					.attr("opacity", (d: any) => {
						return d.isSelected ? 1 : 1;
					})
					.attr("stroke", (d: any) => {
						return d.isSelected ? "red" : "none";
					})
					.attr("stroke-width", (d: any) => {
						return d.isSelected ? 2 : 1;
					});
				const legend = Legend(colorScale, {
					title: "Time till election",
				});
				svg.select(".colorLegend")
					.html(legend?.innerHTML as string)
					.attr(
						"transform",
						`translate(${margin.left},${
							height - margin.bottom + 30
						})`
					);
			} else {
				const minColorDomain = d3.min(data, (d: any) => d.colorField);
				const maxColorDomain = d3.max(data, (d: any) => d.colorField);
				const colorScale = d3
					.scaleDiverging(d3.interpolateRdYlBu)
					.domain([-120000000, 0, maxColorDomain]);

				const onDotMouseOver = function (event: any, d: any) {
					//highlight dot
					d3.select(event.target).attr("r", 6);

					//move tooltip to event position
					const offset = 10;
					const x = event.pageX + offset;
					const y = event.pageY + offset;
					const tooltip = d3.select(".tooltip");
					tooltip
						.transition()
						.duration(200)
						.style("opacity", 0.9)
						.style("display", "block")
						.style("left", x + "px")
						.style("top", y + "px");

					//update tooltip content
					tooltip.html(`${d.comment}`);
				};
				const onDotMouseOut = function (event: any, d: any) {
					//unhighlight dot
					d3.select(event.target).attr("r", 3);

					//hide tooltip
					const tooltip = d3.select(".tooltip");
					tooltip.transition().duration(500).style("opacity", 0)
					.style("display", "none");
				};

				const onDotClick = function (event: any, d: any) {
					//check if alt key is pressed
					let selection = [d.id];
					if (event.altKey) {
						//run inspection event with prev, current and next ids
						const previd = "pre" + d.id;
						const nextid = "nextid" + d.id;
						inspectCallback( d.id);
					}
				}

				plotArea
					.selectAll("circle")
					.data(data)
					.join("circle")
					.on("mouseover", onDotMouseOver)
					.on("mouseout", onDotMouseOut)
					.on("click", onDotClick)
					.transition()
					.duration(300)
					.attr("cx", (d) => xScale(d.x))
					.attr("cy", (d) => yScale(d.y))
					.attr("r", 3)
					.attr("opacity", 0.4)
					.attr("fill", (d: any) => {
						if (d.colorField) {
							return "red";
						} else {
							return "steelblue";
						}
					});
				// .attr("fill", (d:any) => {
				// 	return colorScale(d.colorField);
				// });

				const scaleXCopy = xScale.copy();
				const scaleYCopy = yScale.copy();
				// generator function for zoom
				const zoom = d3
					.zoom()
					.on("zoom", (event) => {
						// applying the zoom transformation to the vertical and horizontal
						// scales
						const rescaledX = event.transform.rescaleX(scaleXCopy);
						const rescaledY = event.transform.rescaleY(scaleYCopy);

						// updating the marks
						plotArea
							.selectAll("circle")
							.transition()

							.attr("cx", (d: any) => rescaledX(d.x))
							.attr("cy", (d: any) => rescaledY(d.y));

						// reconfiguring the axis generators

						// redrawing the axes

						svg.select(".x-axis").call(xAxis, rescaledX, rescaledY);
						svg.select(".y-axis").call(yAxis, rescaledY, rescaledX);
						svg.select(".x-label").call(xLabel, rescaledY);
						svg.select(".y-label").call(yLabel, rescaledX);
					})
					.scaleExtent([1, 30]); // setting the zooming limits;

				svg.call(zoom as any);
			}
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
			<div className="tooltip"></div>
		</div>
	);
}
