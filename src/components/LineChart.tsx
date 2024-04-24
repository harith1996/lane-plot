import React from "react";
import * as d3 from "d3";
import { useD3 } from "../hooks/useD3";
import { LineChartType } from "../types/PlotsTypes";
import { isNull } from "underscore";

type LineChartProps = {
	plot: LineChartType;
	selectionCallback: any;
	selectedIds: string[];
};

function parseAxis(data: any, type: string) {
	switch (type) {
		case "date":
			return parseDateTime(data);
		default:
			return data;
	}
}

function parseDateTime(dateTime: string) {
	const date = new Date(dateTime).toISOString();
	return d3.isoParse(date);
}

export default function LineChart(props: LineChartProps) {
	const columns = ["xAxis", "value", "id"];
	const rawData = props.plot.data;
	const rawSelectedPoints = props.selectedIds;
	const selectionCallback = props.selectionCallback;
	const plot = props.plot;
	const xAxisDType = plot.dataTypes.xAxis;
	const ref = useD3(
		(svg) => {
			//format the data
			const xAxisIdx = columns.indexOf("xAxis");
			const valueIdx = columns.indexOf("value");
			const uniqueIdIdx = columns.indexOf("id");
			const data = rawData.map((d) => {
				//  28/03/2011 15:10
				return {
					xAxis: parseAxis(d.xAxis, xAxisDType)!,
					value: d.value,
					id: d.id,
				};
			});
			const selectedPoints = rawSelectedPoints.map((id) => {
				const dataItem = data.find((item: any) => item["id"] === id);
				return {
					xAxis: dataItem?.xAxis,
					value: dataItem?.value,
					id: dataItem?.id,
				};
			});

			// set the dimensions and margins of the graph
			const margin = { top: 10, right: 30, bottom: 30, left: 60 },
				width = 500,
				height = 500;

			// clear the container

			//append the svg object to the body of the page
			svg.attr("width", width + margin.left + margin.right).attr(
				"height",
				height + margin.top + margin.bottom
			);

			const plotArea = svg
				.select(".container")
				.attr("transform", `translate(${margin.left}, 0)`);

			// Add X axis --> it is a date format
			let x: any = null;
			if (xAxisDType == "date") {
				x = d3
					.scaleTime()
					.domain(
						d3.extent(data, function (d) {
							return d.xAxis as Date;
						}) as [Date, Date]
					)
					.range([0, width])
					.clamp(true);
			} else {
				const ex = d3.extent(data, function (d) {
					return d.xAxis;
				}) as [number, number];
				const exRev = ex.reverse();
				x = d3
					.scaleLinear()
					.domain(exRev)
					.range([0, width])
					.clamp(true);
			}

			const xAxis = (g: any) => {
				g.attr("transform", `translate(0,${height})`);
				if (xAxisDType == "quantitative") {
					const max = x.domain()[0];
					g.call(
						d3.axisBottom(x).tickFormat((d: any, index: number) => {
							return "" + Math.abs((max - d + 1) as number);
						})
					);
				} else {
					g.call(d3.axisBottom(x));
				}

				g.selectAll(".tick text").attr(
					"transform",
					"translate(0,13) rotate(-45)"
				);
				return g;
			};
			const xAxisElement = plotArea
				.select(".x-axis")
				.attr("transform", `translate(${margin.left}, ${height})`)
				.call(xAxis);

			// Add Y axis
			const y = d3
				.scaleLinear()
				.domain([
					0,
					d3.max(data, function (d) {
						return +d.value;
					}) as number,
				])
				.range([height, 0])
				.clamp(true);
			const yAxis = (g: any) => {
				const yTicks: [number, number] = d3.extent(y.domain()) as [
					number,
					number
				];

				return g.call(
					d3.axisLeft(y).tickValues(d3.ticks(...yTicks, height / 80))
				);
			};

			const yAxisElement = plotArea.select(".y-axis").call(yAxis);

			// Add a clipPath: everything out of this area won't be drawn.
			const clip = svg
				.append("defs")
				.append("svg:clipPath")
				.attr("id", "clip")
				.append("svg:rect")
				.attr("width", width)
				.attr("height", height)
				.attr("x", 0)
				.attr("y", 0);

			// Add brushing
			const brush = d3
				.brushX() // Add the brush feature using the d3.brush function
				.extent([
					[0, 0],
					[width, height],
				]) // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
				.on("end", updateChart); // Each time the brush selection changes, trigger the 'updateChart' function

			function getLineGenerator() {
				return d3
					.line()
					.x(function (d: any) {
						return x(d.xAxis);
					})
					.y(function (d: any) {
						return y(d.value);
					})
					.defined((d: any) => !isNull(d.value));
			}
			// Create the line variable: where both the line and the brush take place
			const line = svg
				.select(".plot-area")
				.attr("clip-path", "url(#clip)");

			// Add the line
			line.selectAll("path")
				.datum(data)
				.join("path")
				.attr("class", "line") // I add the class line to be able to modify this line later on.
				.attr("fill", "none")
				.attr("stroke", "steelblue")
				.attr("stroke-width", 1.5)
				.transition()
				.attr("d", getLineGenerator() as any);

			// Add the brushing
			line.append("g").attr("class", "brush").call(brush);

			// A function that set idleTimeOut to null
			let idleTimeout: any;
			function idled() {
				idleTimeout = null;
			}

			plotArea
				.selectAll(".circle-points")
				.data(data)
				.join("circle") // enter append
				.attr("class", "circle-points")
				.transition()
				.attr("r", (d) => {
					return selectedPoints.some((item) => item.id === d.id)
						? 4
						: 1;
				}) // radius
				.attr("cx", (d) => x(d.xAxis)) // center x passing through your xScale
				.attr("cy", (d) => y(d.value)) // center y passing through your yScale
				.attr("fill", (d) => {
					if (d.value === null) {
						return "blue";
					}
					return selectedPoints.some((item) => item.id === d.id)
						? "red"
						: "black";
				})
				.attr("opacity", (d) => {
					return selectedPoints.some((item) => item.id === d.id)
						? 0.6
						: 1;
				})
				.attr("stroke", "black");

			// A function that update the chart for given boundaries
			function updateChart(event: any, d: any) {
				// What are the selected boundaries?
				const extent = event.selection;

				// If no selection, back to initial coordinate. Otherwise, update X axis domain
				if (!extent) {
					if (!idleTimeout)
						return (idleTimeout = setTimeout(idled, 350)); // This allows to wait a little bit
					x.domain([4, 8]);
				} else {
					x.domain([x.invert(extent[0]), x.invert(extent[1])]);
					line.select(".brush").call(brush.move as any, null); // This remove the grey brush area as soon as the selection has been done
				}

				// Update axis and line position
				xAxisElement.transition().duration(1000).call(xAxis);
				line.select(".line")
					.transition()
					.duration(900)
					.attr("d", getLineGenerator() as any);

				// update the points
				plotArea
					.selectAll(".circle-points")
					.transition()
					.duration(1000)
					.attr("cx", (d: any) => x(d.xAxis)) // center x passing through your xScale
					.attr("cy", (d: any) => y(d.value)); // center y passing through your yScale
			}

			// If user double click, reinitialize the chart
			svg.on("dblclick", function () {
				if (xAxisDType == "time") {
					x.domain(
						d3.extent(data, function (d) {
							return d.xAxis;
						}) as [Date, Date]
					);
				} else {
					x.domain(
						d3
							.extent(data, function (d) {
								return d.xAxis;
							})
							.reverse() as [number, number]
					);
				}

				xAxisElement.transition().call(xAxis);
				line.select(".line")
					.transition()
					.duration(900)
					.attr("d", getLineGenerator() as any);
				// update the points
				plotArea
					.selectAll(".circle-points")
					.transition()
					.duration(1000)
					.attr("cx", (d: any) => x(d.xAxis)) // center x passing through your xScale
					.attr("cy", (d: any) => y(d.value)); // center y passing through your yScale
			});
		},
		[plot, rawSelectedPoints]
	);
	return (
		<div>
			<svg ref={ref}>
				<g className="container">
					<g className="plot-area">
						<path className="line"></path>
					</g>
					<g className="x-axis" />
					<g className="y-axis" />
					<text className="x-label" />
					<text className="y-label" />
					<g className="colorLegend" />
				</g>
			</svg>
		</div>
	);
}
