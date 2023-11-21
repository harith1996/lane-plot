/* eslint-disable react-hooks/exhaustive-deps */
import React from "react";
import * as d3 from "d3";
import useDeepCompareEffect from "use-deep-compare-effect";

export const useD3 = (
	renderChartFn: (
		selection: d3.Selection<SVGSVGElement | null, unknown, null, undefined>
	) => void,
	dependencies: any[]
) => {
	const ref = React.useRef<SVGSVGElement>(null);
	useDeepCompareEffect(() => {
		renderChartFn(d3.select(ref.current));
		return () => {};
	}, dependencies);
	return ref;
};
