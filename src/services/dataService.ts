export default class DataService {
	host: string;
	attributes: string[];
	constructor(host: string) {
		this.host = host;
		this.attributes = [];
		this.fetchAttributes().then((data: any) => {
			this.attributes = data;
		});
	}

	fetchAttributes() {
		return fetch(this.host + "/attributes")
			.then((response) => response.json())
			.then((data) => data);
	}

	fetchData() {
		return fetch(this.host + "/preview")
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
