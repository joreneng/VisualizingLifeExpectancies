// Function to render the scatter bubble chart
async function renderScatterBubble(start_year = 1960, end_year = 2023) {
    try {
        const container = document.getElementById('scatterbubble-container');
        if (!container) {
            console.error('Scatter bubble container not found');
            return;
        }

        // Clear previous chart
        d3.select('#scatterbubble-container svg').remove();
        d3.selectAll('#scatter-tooltip').remove();

        if (end_year < 2000) {
            const width = container.clientWidth;
            const height = width * 0.6;

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
                .text(`No health expenditure data available for years ${start_year}-${end_year}`);

            container.appendChild(svg.node());
            return;
        }

        // Fetch data
        const response = await fetch(`http://127.0.0.1:8000/bubble-data/${start_year}/${end_year}`);
        const rawData = await response.json();

        // Helper function to interpolate missing values
        function interpolateValue(data, countryName, date, indicator) {
            const years = Object.keys(data).map(Number).sort((a, b) => a - b);
            const targetDate = Number(date);

            // Find the closest years before and after the target date
            const beforeYear = years.filter(year => year <= targetDate).pop();
            const afterYear = years.filter(year => year > targetDate)[0];

            if (!beforeYear || !afterYear) return null;

            const beforeData = data[beforeYear]?.find(d => d.name === countryName);
            const afterData = data[afterYear]?.find(d => d.name === countryName);

            if (!beforeData || !afterData) return null;

            const beforeValue = beforeData[indicator];
            const afterValue = afterData[indicator];

            if (beforeValue == null || afterValue == null) return null;

            // If exact date match, return the value
            if (beforeYear === targetDate) return beforeValue;
            if (afterYear === targetDate) return afterValue;

            // Interpolate between the two values
            const fraction = (targetDate - beforeYear) / (afterYear - beforeYear);
            return beforeValue + (afterValue - beforeValue) * fraction;
        }

        // Helper function to get interpolated data for a specific year
        function getYearData(data, year) {
            const years = Object.keys(data).map(Number);
            const allCountries = new Set(years.flatMap(year => data[year].map(d => d.name)));

            return Array.from(allCountries).map(countryName => {
                // Find the country's data for this year
                const exactData = data[year]?.find(d => d.name === countryName);
                if (exactData && exactData.health_exp > 0) return exactData;  // Check for positive health_exp

                // If no exact data, interpolate each value
                const health_exp = interpolateValue(data, countryName, year, 'health_exp');
                const life_exp = interpolateValue(data, countryName, year, 'life_exp');
                const population = interpolateValue(data, countryName, year, 'population');

                // Only return if we have all valid values
                if (health_exp > 0 && life_exp && population) {  // Ensure health_exp is positive
                    return {
                        name: countryName,
                        region: data[Object.keys(data)[0]].find(d => d.name === countryName)?.region,
                        health_exp,
                        life_exp,
                        population
                    };
                }
                return null;
            }).filter(d => d != null);
        }

        // Get the container dimensions
        const containerWidth = container.clientWidth;

        // Set up chart properties with responsive dimensions
        const width = Math.min(containerWidth, 800);
        const height = width * 0.6;
        const margin = {
            top: 40, right: 20, bottom: 40, left: 50
        };

        // Create SVG
        const svg = d3.create("svg")
            .attr("viewBox", [0, 0, width, height])
            .attr("width", width)
            .attr("height", height)
            .attr("style", "max-width: 100%; height: auto;");


        // Get all years and interpolated data
        const years = Object.keys(rawData).map(Number).sort(d3.ascending);
        const interpolatedData = {};
        years.forEach(year => {
            interpolatedData[year] = getYearData(rawData, year);
        });

        // Create scales
        const x = d3.scaleLog()
            .domain([Math.max(0.1, d3.min(years.flatMap(year => interpolatedData[year]), d => d.health_exp) * 0.8),
                d3.max(years.flatMap(year => interpolatedData[year]), d => d.health_exp) * 1.2])
            .range([margin.left, width - margin.right]);

        // After creating the SVG, add a clipping path
        svg.append("defs")
            .append("clipPath")
            .attr("id", "chart-area")
            .append("rect")
            .attr("x", margin.left)
            .attr("y", margin.top)
            .attr("width", width - margin.left - margin.right)
            .attr("height", height - margin.top - margin.bottom);

        // Create a group for the chart content with clipping
        const chartGroup = svg.append("g")
            .attr("clip-path", "url(#chart-area)");

        // Update the y scale domain to better contain all values
        const y = d3.scaleLinear()
            .domain([d3.min(years.flatMap(year => interpolatedData[year]), d => d.life_exp) * 0.95,
                d3.max(years.flatMap(year => interpolatedData[year]), d => d.life_exp) * 1.02])
            .range([height - margin.bottom, margin.top]);

        const radius = d3.scaleSqrt()
            .domain([0, d3.max(years.flatMap(year => interpolatedData[year]), d => d.population)])
            .range([4, width / 48]);

        // create a list of keys
        const keys = ["Africa", "Americas", "Europe", "Asia", "Oceania"];

        const color = d3.scaleOrdinal(d3.schemeAccent)
            .domain(Array.from(new Set(years.flatMap(year => interpolatedData[year].map(d => d.region)))));

        // Add one dot in the legend for each name.
        svg.selectAll("mydots")
            .data(keys)
            .enter()
            .append("circle")
            .attr("cy", 10)
            .attr("cx", function (d, i) {
                return margin.left + i * 70;
            })
            .attr("r", 3)
            .attr("stroke", "black")
            .style("fill", function (d) {
                return color(d)
            });

        // Add one dot in the legend for each name.
        svg.selectAll("mylabels")
            .data(keys)
            .enter()
            .append("text")
            .attr("y", 10)
            .attr("x", function (d, i) {
                return margin.left + 7 + i * 70;
            })
            .style("fill", "black")
            .text(function (d) {
                return d;
            })
            .attr("text-anchor", "left")
            .style("alignment-baseline", "middle");

        // Create a group specifically for grid lines (background layer)
        const gridGroup = svg.append("g")
            .attr("class", "grid-group");

        // Add grid lines first (behind everything)
        gridGroup.append("g")
            .attr("class", "grid")
            .attr("stroke", "#ddd")
            .attr("stroke-opacity", 0.1)
            .call(g => g
                .attr("transform", `translate(0,${height - margin.bottom})`)
                .call(d3.axisBottom(x)
                    .ticks(width / 80)
                    .tickSize(-height + margin.top + margin.bottom)
                    .tickFormat("")));

        gridGroup.append("g")
            .attr("class", "grid")
            .attr("stroke", "#ddd")
            .attr("stroke-opacity", 0.1)
            .call(g => g
                .attr("transform", `translate(${margin.left},0)`)
                .call(d3.axisLeft(y)
                    .ticks(height / 50)
                    .tickSize(-width + margin.left + margin.right)
                    .tickFormat("")));

        // Remove grid lines' base lines
        gridGroup.selectAll(".grid .domain").remove();

        // Add axes
        svg.append("g")
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x).ticks(width / 80, ","))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick text")
                .attr("font-family", "Patrick Hand"))
            .call(g => g.append("text")
                .attr("class", "axis-label")
                .attr("x", width - margin.right)
                .attr("y", margin.bottom - 4)
                .attr("fill", "currentColor")
                .attr("text-anchor", "end")
                .text("Current health expenditure (% of GDP) →"));

        svg.append("g")
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick text")
                .attr("font-family", "Patrick Hand"))
            .call(g => g.append("text")
                .attr("x", -margin.left)
                .attr("y", margin.top - 4)
                .attr("class", "axis-label")
                .attr("fill", "currentColor")
                .attr("text-anchor", "start")
                .text("↑ Life expectancy at birth (years)"));

        // Add year label
        const yearLabel = svg.append("text")
            .attr("class", "year-label")
            .attr("x", width - margin.right)
            .attr("y", margin.top + 20)
            .attr("text-anchor", "end")
            .attr("font-size", "24px")
            .attr("font-weight", "bold")
            .attr("font-family", "Patrick Hand");

        // Add tooltip
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .attr("id", "scatter-tooltip")
            .style("opacity", 0)
            .style("position", "absolute")
            .style("background-color", "#E6E6FA")
            .style("border", "solid")
            .style("border-width", "1px")
            .style("border-radius", "5px")
            .style("padding", "10px");

        function updateChart(year) {
            const yearData = interpolatedData[year];

            // Update circles
            const circles = chartGroup.selectAll("circle")
                .data(yearData, d => d.name);

            circles.enter()
                .append("circle")
                .attr("fill", d => color(d.region))
                .attr("opacity", 0.85)
                .attr("stroke", "black")
                .attr("stroke-width", 0.5)
                .merge(circles)
                .transition()
                .duration(250)
                .attr("cx", d => x(d.health_exp))
                .attr("cy", d => y(d.life_exp))
                .attr("r", d => radius(d.population));

            circles.exit().remove();

            chartGroup.selectAll("circle")
                .on("mouseover", function (event, d) {
                    d3.select(this)
                        .attr("stroke-width", 1.5)
                        .attr("opacity", 1);

                    tooltip.style("opacity", 1)
                        .html(`${d.name}<br>
                          Region: ${d.region}<br>
                          Health Exp: ${d.health_exp.toFixed(2)}%<br>
                          Life Exp: ${d.life_exp.toFixed(1)} years<br>
                          Population: ${d3.format(".2s")(d.population)}`)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");
                })
                .on("mouseout", function () {
                    d3.select(this)
                        .attr("stroke-width", 0.5)
                        .attr("opacity", 0.7);
                    tooltip.style("opacity", 0);
                });

            yearLabel.text(year);
        }

        // Animation loop
        let currentYearIndex = 0;

        function animate() {
            if (currentYearIndex >= years.length) {
                currentYearIndex = 0;
            }

            // Skip years with no data
            while (currentYearIndex < years.length &&
            (!interpolatedData[years[currentYearIndex]] ||
                interpolatedData[years[currentYearIndex]].length === 0)) {
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
        d3.selectAll('.tooltip').remove();
        console.error("Error:", error);

        const container = document.getElementById("scatterbubble-container");
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
                .text(`No data available for years ${start_year}-${end_year}`);

            container.appendChild(svg.node());
        }
    }
}

