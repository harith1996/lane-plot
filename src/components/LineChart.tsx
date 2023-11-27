import React from "react";
import * as d3 from "d3";
import { useD3 } from "../hooks/useD3";

function parseDateTime(dateTime : string) {
	const date = new Date(dateTime).toISOString();
	return d3.isoParse(date);
}

export default function LineChart(props : any) {
    const columns = ["time", "value", "unique_id"];
    const rawData = props.data;
    const rawSelectedPoints = props.selectedPoints;
	// const ref = useD3(
	// 	(svg) => {
	// 		//format the data
	// 		const timeIdx = columns.indexOf("time");
	// 		const valueIdx = columns.indexOf("value");
	// 		const uniqueIdIdx = columns.indexOf("unique_id");
	// 		const data = rawData.map((d : any) => {
	// 			//  28/03/2011 15:10
	// 			return {
	// 				date: parseDateTime(d[timeIdx]),
	// 				value: d[valueIdx],
	// 				unique_id: d[uniqueIdIdx],
	// 			};
	// 		});
	// 		const selectedPoints = rawSelectedPoints.map((unique_id : any) => {
	// 			const dataItem = data.find(
	// 				(item : any) => item["unique_id"] === unique_id
	// 			);
	// 			return {
	// 				date: dataItem["date"],
	// 				value: dataItem["value"],
	// 				unique_id: dataItem["unique_id"],
	// 			};
	// 		});

	// 		// set the dimensions and margins of the graph
	// 		const margin = { top: 10, right: 30, bottom: 30, left: 60 },
	// 			width = 960 - margin.left - margin.right,
	// 			height = 550 - margin.top - margin.bottom;

	// 		// clear the container
	// 		svg.selectAll("*").remove();

	// 		//append the svg object to the body of the page
	// 		svg
	// 			.attr("width", width + margin.left + margin.right)
	// 			.attr("height", height + margin.top + margin.bottom)
	// 			.append("g")
	// 			.attr("transform", `translate(${margin.left}, ${margin.top})`);

	// 		// Add X axis --> it is a date format
	// 		const x = d3
	// 			.scaleTime()
	// 			.domain(
	// 				d3.extent(data, function (d) {
	// 					return d.date as Date;
	// 				})
	// 			)
	// 			.range([0, width])
	// 			.clamp(true);
	// 		const xAxis = svg
	// 			.append("g")
	// 			.attr("transform", `translate(0, ${height})`)
	// 			.call(d3.axisBottom(x));

	// 		// Add Y axis
	// 		const y = d3
	// 			.scaleLinear()
	// 			.domain([
	// 				0,
	// 				d3.max(data, function (d) {
	// 					return +d.value;
	// 				}),
	// 			])
	// 			.range([height, 0])
	// 			.clamp(true);
	// 		const yAxis = svg.append("g").call(d3.axisLeft(y));

	// 		// Add a clipPath: everything out of this area won't be drawn.
	// 		const clip = svg
	// 			.append("defs")
	// 			.append("svg:clipPath")
	// 			.attr("id", "clip")
	// 			.append("svg:rect")
	// 			.attr("width", width)
	// 			.attr("height", height)
	// 			.attr("x", 0)
	// 			.attr("y", 0);

	// 		// Add brushing
	// 		const brush = d3
	// 			.brushX() // Add the brush feature using the d3.brush function
	// 			.extent([
	// 				[0, 0],
	// 				[width, height],
	// 			]) // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
	// 			.on("end", updateChart); // Each time the brush selection changes, trigger the 'updateChart' function

	// 		function getLineGenerator() {
	// 			return d3
	// 				.line()
	// 				.x(function (d) {
	// 					return x(d.date);
	// 				})
	// 				.y(function (d) {
	// 					return y(d.value);
	// 				})
	// 				.defined((d) => !isNull(d.value));
	// 		}
	// 		// Create the line variable: where both the line and the brush take place
	// 		const line = svg.append("g").attr("clip-path", "url(#clip)");

	// 		// Add the line
	// 		line.append("path")
	// 			.datum(data)
	// 			.attr("class", "line") // I add the class line to be able to modify this line later on.
	// 			.attr("fill", "none")
	// 			.attr("stroke", "steelblue")
	// 			.attr("stroke-width", 1.5)
	// 			.attr("d", getLineGenerator());

	// 		// Add the brushing
	// 		line.append("g").attr("class", "brush").call(brush);

	// 		// A function that set idleTimeOut to null
	// 		let idleTimeout;
	// 		function idled() {
	// 			idleTimeout = null;
	// 		}

	// 		svg.selectAll(".circle-points")
	// 			.data(data)
	// 			.join("circle") // enter append
	// 			.attr("class", "circle-points")
	// 			.attr("r", (d) => {
	// 				return selectedPoints.some(
	// 					(item) => item.unique_id === d.unique_id
	// 				)
	// 					? 4
	// 					: 1.4;
	// 			}) // radius
	// 			.attr("cx", (d) => x(d.date)) // center x passing through your xScale
	// 			.attr("cy", (d) => y(d.value)) // center y passing through your yScale
	// 			.attr("fill", (d) => {
	// 				if (d.value === null) {
	// 					return "blue";
	// 				}
	// 				return selectedPoints.some(
	// 					(item) => item.unique_id === d.unique_id
	// 				)
	// 					? "red"
	// 					: "black";
	// 			})
	// 			.attr("opacity", (d) => {
	// 				return selectedPoints.some(
	// 					(item) => item.unique_id === d.unique_id
	// 				)
	// 					? 0.6
	// 					: 0.2;
	// 			})
	// 			.attr("stroke", "black");

	// 		// A function that update the chart for given boundaries
	// 		function updateChart(event, d) {
	// 			// What are the selected boundaries?
	// 			const extent = event.selection;

	// 			// If no selection, back to initial coordinate. Otherwise, update X axis domain
	// 			if (!extent) {
	// 				if (!idleTimeout)
	// 					return (idleTimeout = setTimeout(idled, 350)); // This allows to wait a little bit
	// 				x.domain([4, 8]);
	// 			} else {
	// 				x.domain([x.invert(extent[0]), x.invert(extent[1])]);
	// 				line.select(".brush").call(brush.move, null); // This remove the grey brush area as soon as the selection has been done
	// 			}

	// 			// Update axis and line position
	// 			xAxis.transition().duration(1000).call(d3.axisBottom(x));
	// 			line.select(".line")
	// 				.transition()
	// 				.duration(900)
	// 				.attr("d", getLineGenerator());

	// 			// update the points
	// 			svg.selectAll(".circle-points")
	// 				.transition()
	// 				.duration(1000)
	// 				.attr("cx", (d) => x(d.date)) // center x passing through your xScale
	// 				.attr("cy", (d) => y(d.value)); // center y passing through your yScale
	// 		}

	// 		// If user double click, reinitialize the chart
	// 		svg.on("dblclick", function () {
	// 			x.domain(
	// 				d3.extent(data, function (d) {
	// 					return d.date;
	// 				})
	// 			);
	// 			xAxis.transition().call(d3.axisBottom(x));
	// 			line.select(".line")
	// 				.transition()
	// 				.duration(900)
	// 				.attr("d", getLineGenerator());
	// 			// update the points
	// 			svg.selectAll(".circle-points")
	// 				.transition()
	// 				.duration(1000)
	// 				.attr("cx", (d) => x(d.date)) // center x passing through your xScale
	// 				.attr("cy", (d) => y(d.value)); // center y passing through your yScale
	// 		});
	// 	},
	// 	[plot]
	// );
	return (
		<div>
			<svg
				// ref={ref}
				style={{
					height: 1000,
					width: "100%",
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
