async function renderBarChart(start_year = 1960, end_year = 2023) {
    try {
        const container = document.getElementById("bar-container");
        if (!container) {
            throw new Error("Bar chart container not found");
        }

        // Clear previous chart
        d3.select("#bar-container svg").remove();

        // Fetch data
        const response = await fetch(`http://127.0.0.1:8000/bar-chart-data/${start_year}/${end_year}`);
        const data = await response.json();

        // Check if we have any data
        if (Object.keys(data).length === 0) {
            const width = 1000;
            const height = 400;

            const svg = d3.create("svg")
                .attr("viewBox", [0, 0, width, height])
                .attr("width", width)
                .attr("height", height)
                .attr("style", "max-width: 100%; height: auto;");

            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .attr("font-family", "Patrick Hand")
                .attr("font-size", "24px")
                .text(`No mortality data available for years ${start_year}-${end_year}`);

            container.appendChild(svg.node());
            return;
        }

        // Set up dimensions
        const width = 1000;
        const height = 400;
        const marginTop = 100;
        const marginRight = 100;
        const marginBottom = 6;
        const marginLeft = 150;
        const barSize = 60;

        // Create SVG
        const svg = d3.create("svg")
            .attr("viewBox", [0, 0, width, height])
            .attr("width", width)
            .attr("height", height)
            .attr("style", "max-width: 100%; height: auto;");

        // Create scales
        const x = d3.scaleLinear([0, 100], [marginLeft, width - marginRight]);
        const y = d3.scaleBand()
            .domain([0, 1, 2])
            .range([marginTop, marginTop + 3 * barSize])
            .padding(0.1);

        const colorScale = d3.scaleOrdinal()
            .domain(["Communicable Diseases", "Injuries", "Non-communicable Diseases"])
            .range(["#b3dee2", "#c8b6ff", "#ffafcc"]);

        // Add axes
        const xAxis = d3.axisTop(x).tickFormat(d => d + "%");
        svg.append("g")
            .style("font-family", "Patrick Hand")
            .style("font-size", "25px")
            .attr("transform", `translate(0,${marginTop})`)
            .call(xAxis)
            .call(g => g.select(".domain").remove());

        // Group data by year
        const dataByYear = d3.group(data, d => d.date);

        function updateChart(year) {
            const yearData = dataByYear.get(year);

            // Handle no data case
            if (!yearData || yearData.length === 0) {
                // Clear existing elements
                svg.selectAll("rect").remove();
                svg.selectAll(".label").remove();

                // Update year display to show no data
                svg.selectAll(".year-label")
                    .data([year])
                    .join("text")
                    .attr("class", "year-label")
                    .attr("x", width - marginRight)
                    .attr("y", height - marginBottom)
                    .attr("text-anchor", "end")
                    .attr("font-weight", "bold")
                    .attr("font-size", "50px")
                    .text(d => `${d} (No data)`);
                return;
            }

            yearData.sort((a, b) => b.value - a.value);

            // Update bars
            const bars = svg.selectAll("rect")
                .data(yearData, d => d.name);

            bars.enter()
                .append("rect")
                .attr("fill", d => colorScale(d.name))
                .attr("height", y.bandwidth())
                .merge(bars)
                .transition()
                .duration(250)
                .attr("x", x(0))
                .attr("y", (d, i) => y(i))
                .attr("width", d => x(d.value) - x(0));

            // Update labels
            const labels = svg.selectAll(".label")
                .data(yearData, d => d.name);

            labels.enter()
                .append("text")
                .attr("class", "label")
                .attr("dy", "0.35em")
                .merge(labels)
                .transition()
                .duration(250)
                .attr("x", d => x(d.value) + 10)
                .attr("y", (d, i) => y(i) + y.bandwidth() / 2)
                .text(d => `${d.name}: ${d.value.toFixed(1)}%`);

            // Update year display
            svg.selectAll(".year-label")
                .data([year])
                .join("text")
                .attr("class", "year-label")
                .attr("x", width - marginRight)
                .attr("y", height - marginBottom)
                .attr("text-anchor", "end")
                .attr("font-weight", "bold")
                .attr("font-size", "50px")
                .text(d => d);
        }

        // Animation
        const years = Array.from(dataByYear.keys()).sort(d3.ascending);
        let currentYearIndex = 0;

        function animate() {
            if (currentYearIndex >= years.length) {
                currentYearIndex = 0;
            }

            // Skip years with no data
            while (currentYearIndex < years.length &&
            (!dataByYear.get(years[currentYearIndex]) ||
                dataByYear.get(years[currentYearIndex]).length === 0)) {
                currentYearIndex++;
                if (currentYearIndex >= years.length) {
                    currentYearIndex = 0;
                }
            }

            updateChart(years[currentYearIndex]);
            currentYearIndex++;
            setTimeout(animate, 1000);
        }

        animate();
        container.appendChild(svg.node());

    } catch (error) {
        console.error("Error:", error);

        const container = document.getElementById("bar-container");
        if (container) {
            const width = 1000;
            const height = 400;

            const svg = d3.create("svg")
                .attr("viewBox", [0, 0, width, height])
                .attr("width", width)
                .attr("height", height)
                .attr("style", "max-width: 100%; height: auto;");

            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("text-anchor", "middle")
                .attr("font-family", "Patrick Hand")
                .attr("font-size", "24px")
                .text(`No mortality data available for years ${start_year}-${end_year}`);

            container.appendChild(svg.node());
        }
    }
}

