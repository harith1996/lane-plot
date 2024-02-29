import { LaNePlotFilters } from "../types/FilterTypes";

export default class DataService {
	host: string;
	attributes: string[];
	initPromise: Promise<boolean>;
	defaultFetchAttributes: string[];
	constructor(host: string) {
		this.host = host;
		this.attributes = [];
		this.initPromise = this.initialize();
		this.defaultFetchAttributes = ["unique_id"];
	}

	initialize() {
		return this.fetchAttributes().then((attributes) => {
			this.attributes = attributes;
			return true;
		});
	}

	fetchFilterOptions(filterMap: LaNePlotFilters) {
		const reqBody = JSON.stringify(filterMap);

		return fetch(this.host + "/filters", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: reqBody,
		}).then((response) => response.json());
	}

	fetchAttributes() {
		return fetch(this.host + "/attributes")
			.then((response) => response.json())
			.then((data) => data);
	}

	fetchData(
		filterColumn: string = "event_user_id",
		filterValue: string = "15996738",
		shownPlot: string = "revision_text_bytes",
		linearizeBy: string = "timestamp",
		extraColumns: string[] = []
	) {
		const xLabel = ["diffNext", shownPlot].join("_");
		const yLabel = ["diffPrev", shownPlot].join("_");
		const reqAttributes = this.defaultFetchAttributes
			.concat([
				xLabel,
				yLabel,
				shownPlot,
				linearizeBy,
				extraColumns.join(","),
			])
			.join(",");
		return fetch(
			this.host +
				`/get-data?filterColumn=${filterColumn}&filterValue=${filterValue}&attributes=${reqAttributes}`
		)
			.then((response) => response.json())
			.then((data) => {
				return { data, reqAttributes, shownPlot, linearizeBy };
			});
	}

	scatterplotifyData(
		data: any,
		xField: string,
		yField: string,
		idField: string,
		colorField: string,
		attList: string[]
	) {
		let xIndex = attList.indexOf(xField);
		let yIndex = attList.indexOf(yField);
		let idIndex = attList.indexOf(idField);
		let colorIndex = attList.indexOf(colorField);
		let otherFields = attList.filter(
			(att) =>
				att !== xField &&
				att !== yField &&
				att !== idField &&
				att !== colorField
		);
		let out = [];
		for (let i = 0; i < data.length; i++) {
			let outItem = {
				x: data[i][xIndex],
				y: data[i][yIndex],
				colorField: data[i][colorIndex],
				id: data[i][idIndex],
			};
			otherFields.forEach((field) => {
				Object.defineProperty(outItem, field, {
					value: data[i][attList.indexOf(field)],
					writable: false,
				});
			});
			out.push(outItem);
		}
		return out;
	}

	linechartifyData(
		data: any,
		xField: string,
		yField: string,
		idField: string,
		attList: string[]
	) {
		let xIndex = attList.indexOf(xField);
		let yIndex = attList.indexOf(yField);
		let idIndex = attList.indexOf(idField);
		let out = [];
		for (let i = 0; i < data.length; i++) {
			out.push({
				date: data[i][xIndex],
				value: data[i][yIndex],
				id: data[i][idIndex],
			});
		}
		return out;
	}

	fetchHumanReadableEntityName(fieldName: string, fieldValue: string) {
		//fetch from server
		return fetch(this.host + `/get-human-readable-name?fieldName=${fieldName}&fieldValue=${fieldValue}`, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
			}
		}).then((response) =>
			response.json().then((data) => data.humanReadableName)
		);
	}
}
