async function renderLineChart(start_year = 1960, end_year = 2023) {
    try {
        const container = document.getElementById("line-container");
        if (!container) {
            throw new Error("Line chart container not found");
        }

        // Clear previous chart
        d3.select("#line-container svg").remove();

        // Fetch data
        const response = await fetch(`http://127.0.0.1:8000/line-chart-data/${start_year}/${end_year}`);
        const data = await response.json();

        // Set up dimensions
        const width = container.clientWidth;
        const height = Math.min(width * 0.6, 600);
        const marginTop = 20;
        const marginRight = 20;
        const marginBottom = 30;
        const marginLeft = 50;

        // Create scales
        const x = d3.scaleLinear()
            .domain(d3.extent(data, d => d.date))
            .range([marginLeft, width - marginRight]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value)]).nice()
            .range([height - marginBottom, marginTop]);

        // Create SVG
        const svg = d3.select("#line-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .attr("style", "max-width: 100%; height: auto; overflow: visible; font: 10px sans-serif;");

        // Add axes
        svg.append("g")
            .attr("transform", `translate(0,${height - marginBottom})`)
            .call(d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick text")
                .attr("font-family", "Patrick Hand"))
            .call(g => g.append("text")
                .attr("class", "axis-label")
                .attr("x", width - marginRight)
                .attr("y", marginBottom - 4)
                .attr("fill", "currentColor")
                .attr("text-anchor", "end")
                .text("Year →"));

        svg.append("g")
            .attr("transform", `translate(${marginLeft},0)`)
            .call(d3.axisLeft(y))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick text")
                .attr("font-family", "Patrick Hand"))
            .call(g => g.selectAll(".tick line").clone()
                .attr("x2", width - marginLeft - marginRight)
                .attr("stroke-opacity", 0.1))
            .call(g => g.append("text")
                .attr("x", -marginLeft)
                .attr("y", 10)
                .attr("class", "axis-label")
                .attr("fill", "currentColor")
                .attr("text-anchor", "start")
                .text("↑ Life Expectancy at birth (years)"));

        // Group data by country
        const groupedData = d3.group(data, d => d.name);

        // Create line generator
        const line = d3.line()
            .x(d => x(d.date))
            .y(d => y(d.value));

        // Draw lines
        const paths = svg.append("g")
            .attr("fill", "none")
            .attr("stroke", "#8E6DBF")
            .attr("stroke-width", 1.5)
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .selectAll("path")
            .data(groupedData)
            .join("path")
            .style("mix-blend-mode", "multiply")
            .attr("d", ([_, values]) => line(values));

        // Create array of all points for interaction
        const allPoints = Array.from(groupedData).flatMap(([country, values]) =>
            values.map(d => ({...d, country}))
        );

        // Add invisible dots for hover interaction
        const dots = svg.append("g")
            .attr("display", "none");

        dots.append("circle")
            .attr("r", 4)
            .attr("fill", "#8E6DBF");

        dots.append("text")
            .attr("text-anchor", "middle")
            .attr("y", -8);

        // Add interactive overlay
        svg.append("rect")
            .attr("width", width)
            .attr("height", height)
            .attr("fill", "none")
            .attr("pointer-events", "all")
            .on("mousemove", mousemoved)
            .on("mouseenter", mouseentered)
            .on("mouseleave", mouseleft);

        function mouseentered() {
            paths.style("mix-blend-mode", null)
                .style("stroke", "#ddd");
            dots.attr("display", null);
        }

        function mousemoved(event) {
            const [xm, ym] = d3.pointer(event);
            const closestPoint = d3.least(allPoints, d => {
                const dx = x(d.date) - xm;
                const dy = y(d.value) - ym;
                return dx * dx + dy * dy;
            });

            if (closestPoint) {
                dots.attr("transform", `translate(${x(closestPoint.date)},${y(closestPoint.value)})`)
                    .select("text").text(`${closestPoint.name}: ${closestPoint.value.toFixed(2)}`)
                    .style("font-family", "Patrick Hand");

                paths.style("stroke", d => d[0] === closestPoint.country ? "#8E6DBF" : "#ddd")
                    .filter(d => d[0] === closestPoint.country)
                    .raise();
            }
        }

        function mouseleft() {
            paths.style("mix-blend-mode", "multiply")
                .style("stroke", "#8E6DBF");
            dots.attr("display", "none");
        }

        container.appendChild(svg.node());

    } catch (error) {
        console.error("Error:", error);
    }
}
