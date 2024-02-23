import * as React from "react";
import { useState, ChangeEvent } from "react";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";

type RadioGroupProps = {
	label: string;
	options: string[];
	value: string;
	onChange: (value: string) => void;
};

export default function CustomRadioGroup(props: RadioGroupProps) {

	const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
		props.onChange((event.target as HTMLInputElement).value);
	};

	return (
		<FormControl>
			<FormLabel id="demo-controlled-radio-buttons-group">
				{props.label}
			</FormLabel>
			<RadioGroup
				aria-labelledby="demo-controlled-radio-buttons-group"
				name="controlled-radio-buttons-group"
				value={props.value}
				onChange={handleChange}
			>
				{props.options.map((option, index) => (
					<FormControlLabel
						key={index}
						value={option}
						control={<Radio />}
						label={option}
					/>
				))}
			</RadioGroup>
		</FormControl>
	);
}
