// chloropleth-chart.js
async function renderChloropleth() {
    try {
        // Fetch the data from FastAPI
        const response = await fetch('http://127.0.0.1:8000/avg-values');
        const data = await response.json();

        // Fetch and parse TopoJSON (Countries data)
        const world = await d3.json('../data/world-topo.json');
        const countries = topojson.feature(world, world.objects.countries);
        const countrymesh = topojson.mesh(world, world.objects.countries, (a, b) => a !== b);

        // Call the function to create the chart with the fetched data
        createChloropleth(data, countries, countrymesh);
    } catch (error) {
        console.error('Error fetching data or parsing TopoJSON:', error);
    }
}

function createChloropleth(data, countries, countrymesh) {
    const width = 928;
    const marginTop = 46;
    const height = width / 2 + marginTop;

    const projection = d3.geoEqualEarth().fitExtent([[2, marginTop + 2], [width - 2, height]], {type: "Sphere"});
    const path = d3.geoPath(projection);

    // Define the color scale based on the fetched data
    const color = d3.scaleSequential(d3.extent(Object.values(data)), d3.interpolateHsl(d3.hsl("#f9035e"), d3.hsl("#5fc52e")));

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    // Append the legend
    svg.append("g")
        .attr("transform", "translate(20,0)")
        .append(() => Legend(color, {title: "Average Life Expectancy (years)", width: 260}));

    // Add a white sphere with a black border (the globe background)
    svg.append("path")
        .datum({type: "Sphere"})
        .attr("fill", "white")
        .attr("stroke", "currentColor")
        .attr("d", path);

      // Tooltip div (hidden by default)
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background-color", "rgba(0, 0, 0, 0.7)")
        .style("color", "white")
        .style("padding", "5px")
        .style("border-radius", "5px")
        .style("pointer-events", "none");

    // Render countries' paths and apply color based on data
    svg.append("g")
        .selectAll("path")
        .data(countries.features)  // Use TopoJSON features
        .join("path")
        .attr("fill", d => {
            const countryCode = d.properties.countryCode;
            const avgValue = data[countryCode];  // Map data to countries by name
            return avgValue ? color(avgValue) : "#959595";  // Default grey if no data
        })
        .attr("d", path)
        .on("mouseover", function(event, d) {
            // Show tooltip on hover
            const countryName = d.properties.name;
            const countryCode = d.properties.countryCode;
            const avgValue = data[countryCode];

            tooltip.html(`${countryName}<br>Average Life Expectancy: ${avgValue ? avgValue.toFixed(2) : "Data not available"}`)
                .style("visibility", "visible");
        })
        .on("mousemove", function(event) {
            // Position the tooltip based on mouse location
            tooltip.style("top", (event.pageY + 10) + "px")
                .style("left", (event.pageX + 10) + "px");
        })
        .on("mouseout", function() {
            // Hide tooltip when mouse leaves the country
            tooltip.style("visibility", "hidden");
        })
        .append("title")
        .text(d => {
            const countryName = d.properties.name;
            const avgValue = data[countryName];
            return `${countryName}\n${avgValue ? avgValue.toFixed(2) : "Data not available"}`;
        });

    // Add a white mesh for country borders
    svg.append("path")
        .datum(countrymesh)
        .attr("fill", "none")
        .attr("stroke", "white")
        .attr("d", path);

    // Append the SVG element to the chart container
    document.getElementById('chloro-container').appendChild(svg.node());
}

window.onload = renderChloropleth;

