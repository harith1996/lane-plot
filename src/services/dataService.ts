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
			body: reqBody
		}).then((response) =>
			response.json()
		);
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
		linearizeBy: string = "event_timestamp"
	) {
		const xLabel = ["diffNext", shownPlot].join("_");
		const yLabel = ["diffPrev", shownPlot].join("_");
		const reqAttributes = this.defaultFetchAttributes
			.concat([xLabel, yLabel, shownPlot, linearizeBy])
			.join(",");
		return fetch(
			this.host +
				`/get-data?filterColumn=${filterColumn}&filterValue=${filterValue}&attributes=${reqAttributes}`
		)
			.then((response) => response.json())
			.then((data) => {
				return { data, reqAttributes, shownPlot };
			});
	}

	scatterplotifyData(data: any, xField: string, yField: string, idField:string, attList: string[]) {
		let xIndex = attList.indexOf(xField);
		let yIndex = attList.indexOf(yField);
		let idIndex = attList.indexOf(idField);
		let out = [];
		for (let i = 0; i < data.length; i++) {
			out.push({ x: data[i][xIndex], y: data[i][yIndex], id: data[i][idIndex] });
		}
		return out;
	}

	linechartifyData(data: any, xField: string, yField: string, idField:string, attList: string[]) {
		let xIndex = attList.indexOf(xField);
		let yIndex = attList.indexOf(yField);
		let idIndex = attList.indexOf(idField);
		let out = [];
		for (let i = 0; i < data.length; i++) {
			out.push({ date: data[i][xIndex], value: data[i][yIndex], id: data[i][idIndex] });
		}
		return out;
	}
}
