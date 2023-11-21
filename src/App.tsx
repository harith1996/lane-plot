import React, { useEffect } from "react";
import "./App.css";
import MultiSelect from "./components/MultiSelect";
import Scatterplot from "./components/Scatterplot";
import SingleSelect from "./components/SingleSelect";

function App() {
  const [selected1, setSelected1] = React.useState<string>("");
  let options1 = ["option1", "option2", "option3", "option4"];
  let defaultValue1 = "option1";
  let label1 = "label1";
  const onChange1 = (value: string) => {
    setSelected1(value)
  };
  return (
    <div className="App">
      <div>
        Filters
      <SingleSelect options={options1} onChange={onChange1} label={label1} selectedValue={selected1}></SingleSelect>
      </div>
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
