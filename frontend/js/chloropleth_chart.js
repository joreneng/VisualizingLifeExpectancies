// chloropleth_chart.js
async function renderChloropleth(start_year = 1960, end_year = 2023) {
    try {
        const container = document.getElementById("chloro-container");
        if (!container) {
            throw new Error("Chloropleth container not found");
        }

        // Clear previous chart
        d3.select("#chloro-container svg").remove();
        d3.selectAll("#chloro-tooltip").remove();

        // Fetch data
        const response = await fetch(`http://127.0.0.1:8000/chloro-chart-data/${start_year}/${end_year}`);
        const data = await response.json();

        // Fetch and parse TopoJSON
        const world = await d3.json("../data/world-topo.json");
        const countries = topojson.feature(world, world.objects.countries);
        const countrymesh = topojson.mesh(world, world.objects.countries, (a, b) => a !== b);

        // Set up dimensions
        const containerWidth = container.clientWidth;
        const width = Math.min(containerWidth - 40, 800);
        const marginTop = 46;
        const height = (width / 2) + marginTop;

        const projection = d3.geoEqualEarth()
            .fitExtent([[2, marginTop + 2], [width - 2, height]], {type: "Sphere"});
        const path = d3.geoPath(projection);

        // Define color scale
        const color = d3.scaleSequential(d3.extent(Object.values(data)), 
            d3.interpolateHsl(d3.hsl("#ff8fa3"), d3.hsl("#8ac926")));

        // Create SVG
        const svg = d3.create("svg")
            .attr("viewBox", [0, 0, width, height])
            .attr("style", "max-width: 100%; height: auto;");

        // Append legend
        svg.append("g")
            .attr("transform", "translate(20,0)")
            .append(() => Legend(color, {
                title: "Average Life Expectancy (years)", 
                width: 260
            }));

        // Add globe background
        svg.append("path")
            .datum({type: "Sphere"})
            .attr("fill", "white")
            .attr("stroke", "currentColor")
            .attr("d", path);

        // Create tooltip
        const tooltip = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
            .attr("id", "chloro-tooltip")
            .style("position", "absolute")
            .style("visibility", "hidden")
            .style("background-color", "#E6E6FA")
            .style("border", "solid")
            .style("padding", "5px")
            .style("border-width", "1px")
            .style("border-radius", "5px")
            .style("pointer-events", "none");

        // Render countries
        svg.append("g")
            .selectAll("path")
            .data(countries.features)
            .join("path")
            .attr("fill", d => {
                const countryCode = d.properties.countryCode;
                const avgValue = data[countryCode];
                return avgValue ? color(avgValue) : "#959595";
            })
            .attr("d", path)
            .on("mouseover", function(event, d) {
                const countryName = d.properties.name;
                const countryCode = d.properties.countryCode;
                const avgValue = data[countryCode];

                tooltip.html(`${countryName}<br>Average Life Expectancy: ${avgValue ? avgValue.toFixed(2) : "Data not available"}`)
                    .style("visibility", "visible");
            })
            .on("mousemove", function(event) {
                tooltip.style("top", (event.pageY + 10) + "px")
                    .style("left", (event.pageX + 10) + "px");
            })
            .on("mouseout", function() {
                tooltip.style("visibility", "hidden");
            })
            .append("title");

        // Add country borders
        svg.append("path")
            .datum(countrymesh)
            .attr("fill", "none")
            .attr("stroke", "white")
            .attr("d", path);

        container.appendChild(svg.node());

    } catch (error) {
        console.error("Error:", error);
    }
}
