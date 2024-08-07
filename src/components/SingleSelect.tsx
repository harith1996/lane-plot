import * as React from "react";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import { FormHelperText } from '@mui/material';
import Select, { SelectChangeEvent } from "@mui/material/Select";

type SingleSelectProps = {
	selectedValue: string;
	label: string;
	options: string[];
	helperText?: string;
	onChange: (value: string) => void;
};

export default function SelectAutoWidth(props: SingleSelectProps) {
	const handleChange = (event: SelectChangeEvent) => {
		props.onChange(event.target.value as string);
	};
		

	return (
		<div>
			<FormControl sx={{ m: 1, minWidth: 80 }}>
				<InputLabel id="demo-simple-select-autowidth-label">
					{props.label}
				</InputLabel>
				<Select
					labelId="demo-simple-select-autowidth-label"
					id="demo-simple-select-autowidth"
					value={props.selectedValue}
					onChange={handleChange}
					autoWidth
					label={props.label}
				>
					{props.options.map((option) => {
						return (
							<MenuItem key={option} value={option}>
								{option}
							</MenuItem>
						);
					})}
				</Select>
				<FormHelperText>{props.helperText}</FormHelperText>
			</FormControl>
		</div>
	);
}
