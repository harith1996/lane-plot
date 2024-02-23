# LaNe Plot: A transformation for visualizing time-series data

LaNe Plot is a scatterplot for visualizing time-series data. Each data point in the time-series is plotted based on the difference in value between its neighbors. This allows smaller patterns that are not visible on a line chart to be revealed and analyzed. See the figure below a design sketch.

![LaNe Plot](src/static/images/quadrant_labels.drawio.png)

## Example dataset: Wikipedia revisions

We took a dataset of Wikipedia revisions and extracted a time series of the size of each edit. This time series was then visualized using LaNe Plot. See the figure below for an example:

![Wiki Revisions](src/static/images/wikipedia_label_quadrants_v2.png)

To run the app, clone the repository and run the following commands:

### `npm install`
### `cd backend_temp/python`
### `pip install -r requirements.txt`
### `cd ../../`
### `npm run dev`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

Written in TypeScript and Python. Built with React, Flask, and D3.js.

## License : CC BY 4.0 DEED
This license enables reusers to distribute, remix, adapt, and build upon the material in any medium or format, so long as attribution is given to the creator. The license allows for commercial use. Refer https://creativecommons.org/licenses/by/4.0/