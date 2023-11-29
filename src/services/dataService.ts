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

	fetchFilterOptions(endpoints: string) {
		return fetch(this.host + "/" + endpoints).then((response) =>
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
		shownPlot: string = "revision_text_bytes"
	) {
		const xLabel = ["diffNext", shownPlot].join("_");
		const yLabel = ["diffPrev", shownPlot].join("_");
		const reqAttributes = this.defaultFetchAttributes
			.concat([xLabel, yLabel])
			.join(",");
		return fetch(
			this.host +
				`/get-data?filterColumn=${filterColumn}&filterValue=${filterValue}&attributes=${reqAttributes}`
		)
			.then((response) => response.json())
			.then((data) => {
				return { data, reqAttributes };
			});
	}

	plotsifyData(data: any, xField: string, yField: string, attList: string[]) {
		let xIndex = attList.indexOf(xField);
		let yIndex = attList.indexOf(yField);
		let out = [];
		for (let i = 0; i < data.length; i++) {
			out.push({ x: data[i][xIndex], y: data[i][yIndex] });
		}
		return out;
	}
}
