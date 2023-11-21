import React from "react";
import "./App.css";
import MultiSelect from "./components/MultiSelect";
import Scatterplot from "./components/Scatterplot";

function App() {
  return (
    <div className="App">
      <div>Filters</div>
      <div>
        <MultiSelect></MultiSelect>
      </div>
      <div>
        <Scatterplot></Scatterplot>
      </div>
    </div>
  );
}

export default App;
