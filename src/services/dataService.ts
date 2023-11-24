export default class DataService {
	host: string;
	attributes: string[];
	initPromise: Promise<boolean>;
	constructor(host: string) {
		this.host = host;
		this.attributes = [];
		this.initPromise = this.initialize();
	}

	initialize() {
		return this.fetchAttributes().then((attributes) => {
			this.attributes = attributes;
			return true;
		});
	}

	fetchAttributes() {
		return fetch(this.host + "/attributes")
			.then((response) => response.json())
			.then((data) => data);
	}

	fetchData(
		filterColumn: string = "page_id",
		filterValue: string = "68401269",
		attributes: string[] = ["page_title_historical"]
	) {
		const reqAttributes = attributes.join(",");
		return fetch(
			this.host +
				`/get-data?filterColumn=${filterColumn}&filterValue=${filterValue}&attributes=${reqAttributes}`
		)
			.then((response) => response.json())
			.then((data) => data);
	}

	plotsifyData(data: any, xField: string, yField: string) {
		let xIndex = this.attributes.indexOf(xField);
		let yIndex = this.attributes.indexOf(yField);
		let out = [];
		for (let i = 0; i < data.length; i++) {
			out.push({ x: data[i][xIndex], y: data[i][yIndex] });
		}
		return out;
	}
}
