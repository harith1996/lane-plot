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

function parseDateTime(dateTime: string) {
	const date = new Date(dateTime).toISOString();
	return d3.isoParse(date);
}

export default function LineChart(props: LineChartProps) {
	const columns = ["date", "value", "id"];
	const rawData = props.plot.data;
	const rawSelectedPoints = props.selectedIds;
	const selectionCallback = props.selectionCallback;
	const plot = props.plot;
	const ref = useD3(
		(svg) => {
			//format the data
			const timeIdx = columns.indexOf("date");
			const valueIdx = columns.indexOf("value");
			const uniqueIdIdx = columns.indexOf("id");
			const data = rawData.map((d) => {
				//  28/03/2011 15:10
				return {
					date: parseDateTime(d.date)!,
					value: d.value,
					id: d.id,
				};
			});
			const selectedPoints = rawSelectedPoints.map((id) => {
				const dataItem = data.find(
					(item: any) => item["id"] === id
				);
				return {
					date: dataItem?.date,
					value: dataItem?.value,
					id: dataItem?.id,
				};
			});

			// set the dimensions and margins of the graph
			const margin = { top: 10, right: 30, bottom: 30, left: 60 },
				width = 700 - margin.left - margin.right,
				height = 300 - margin.top - margin.bottom;

			// clear the container

			//append the svg object to the body of the page
			svg
				.attr("width", width + margin.left + margin.right)
				.attr("height", height + margin.top + margin.bottom)
				.attr("transform", `translate(${margin.left}, ${margin.top})`);

			// Add X axis --> it is a date format
			const x = d3
				.scaleTime()
				.domain(
					d3.extent(data, function (d) {
						return d.date as Date;
					}) as [Date, Date]
				)
				.range([0, width])
				.clamp(true);
			const xAxis = (g: any) => {
				return g
					.attr("transform", `translate(0,${height})`)
					.call(d3.axisBottom(x));
			};
			const xAxisElement = svg
				.select(".x-axis")
				.attr("transform", `translate(0, ${height})`)
				.call(xAxis);

			// Add Y axis
			const y = d3
				.scaleSymlog()
				.domain([
					0,
					d3.max(data, function (d) {
						return +d.value;
					}) as number,
				])
				.range([height, 0])
				.clamp(true);
			const yAxis = (g: any) => {
				return g.call(d3.axisLeft(y));
			};
			const yAxisElement = svg.select(".y-axis").call(yAxis);

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
						return x(d.date);
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

			svg.selectAll(".circle-points")
				.data(data)
				.join("circle") // enter append
				.attr("class", "circle-points")
				.transition()
				.attr("r", (d) => {
					return selectedPoints.some(
						(item) => item.id === d.id
					)
						? 4
						: 1.4;
				}) // radius
				.attr("cx", (d) => x(d.date)) // center x passing through your xScale
				.attr("cy", (d) => y(d.value)) // center y passing through your yScale
				.attr("fill", (d) => {
					if (d.value === null) {
						return "blue";
					}
					return selectedPoints.some(
						(item) => item.id === d.id
					)
						? "red"
						: "black";
				})
				.attr("opacity", (d) => {
					return selectedPoints.some(
						(item) => item.id === d.id
					)
						? 0.6
						: 0.2;
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
				svg.selectAll(".circle-points")
					.transition()
					.duration(1000)
					.attr("cx", (d: any) => x(d.date)) // center x passing through your xScale
					.attr("cy", (d: any) => y(d.value)); // center y passing through your yScale
			}

			// If user double click, reinitialize the chart
			svg.on("dblclick", function () {
				x.domain(
					d3.extent(data, function (d) {
						return d.date;
					}) as [Date, Date]
				);
				xAxisElement.transition().call(xAxis);
				line.select(".line")
					.transition()
					.duration(900)
					.attr("d", getLineGenerator() as any);
				// update the points
				svg.selectAll(".circle-points")
					.transition()
					.duration(1000)
					.attr("cx", (d: any) => x(d.date)) // center x passing through your xScale
					.attr("cy", (d: any) => y(d.value)); // center y passing through your yScale
			});
		},
		[plot, rawSelectedPoints]
	);
	return (
		<div>
			<svg
				ref={ref}
			>
				<g className="plot-area">
					<path className="line"></path>
				</g>
				<g className="x-axis" />
				<text className="x-label" />
				<text className="y-label" />
				<g className="y-axis" />
				<g className="colorLegend" />
			</svg>
		</div>
	);
}
