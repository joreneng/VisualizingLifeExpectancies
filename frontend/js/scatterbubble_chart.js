// Parse a series of data values into a usable format
function parseSeries(series) {
  return series.map(([year, value]) => [new Date(Date.UTC(year, 0, 1)), value]);
}

// Linear interpolation function
function interpolateMissingValues(data) {
  const interpolate = (key) => {
    for (let countryName in data) {
      const country = countryName
      const values = data[country];
      
      // Convert array of DateValue objects to sorted array of [date, value]
      let timePoints = values
        .filter(point => point.value !== null)  // Filter out null values
        .map(point => [point.date, point.value])
        .sort((a, b) => a[0] - b[0]);

      // Interpolate missing values
      let interpolatedValues = [];
      for (let i = 0; i < timePoints.length - 1; i++) {
        const [date1, value1] = timePoints[i];
        const [date2, value2] = timePoints[i + 1];

        // Add the current point
        interpolatedValues.push({ date: date1, value: value1 });

        // Fill in missing dates between current and next point
        for (let date = date1 + 1; date < date2; date++) {
          const fraction = (date - date1) / (date2 - date1);
          const interpolatedValue = value1 + (value2 - value1) * fraction;
          interpolatedValues.push({ date: date, value: interpolatedValue });
        }
      }

      // Add the last point
      if (timePoints.length > 0) {
        const lastPoint = timePoints[timePoints.length - 1];
        interpolatedValues.push({ date: lastPoint[0], value: lastPoint[1] });
      }

      // Update the country's data with interpolated values
      country[key] = interpolatedValues;
    }
  };

  // Interpolate each indicator
  interpolate('health_exp');
  interpolate('life_exp');
  interpolate('population');
  
  return data;
}

// Helper function to get data at a specific date
function dataAt(data, date) {
  const years = Object.keys(data).map(Number); 
  const allCountries = new Set(years.flatMap(year => data[year].map(d => d.name)));
  
  return Array.from(allCountries).map(countryName => {
    // Find the country's data for this date
    const countryData = data[date]?.find(d => d.name === countryName);
    if (countryData) return countryData;

    // If no data found, interpolate
    return {
      name: countryName,
      region: findRegion(data, countryName),
      health_exp: valueAt(data, countryName, 'health_exp', date),
      life_exp: valueAt(data, countryName, 'life_exp', date),
      population: valueAt(data, countryName, 'population', date)
    };
  });
}

// Helper function to find a country's region
function findRegion(data, countryName) {
  for (const year of Object.keys(data)) {
    const countryData = data[year].find(d => d.name === countryName);
    if (countryData) return countryData.region;
  }
  return null;
}

// Function to get value at a specific date using interpolation
function valueAt(data, countryName, indicator, targetDate) {
  // Get all available dates
  const dates = Object.keys(data).map(Number);  // No need to sort
  
  // Find the data points before and after the target date
  const beforeDate = dates.filter(d => d <= targetDate).pop();
  const afterDate = dates.filter(d => d >= targetDate)[0];

  if (!beforeDate || !afterDate) return null;

  const beforeValue = data[beforeDate].find(d => d.name === countryName)?.[indicator];
  const afterValue = data[afterDate].find(d => d.name === countryName)?.[indicator];

  if (beforeValue == null || afterValue == null) return null;

  // If exact date match, return the value
  if (beforeDate === targetDate) return beforeValue;
  if (afterDate === targetDate) return afterValue;

  // Interpolate between the two values
  const fraction = (targetDate - beforeDate) / (afterDate - beforeDate);
  return beforeValue + (afterValue - beforeValue) * fraction;
}

// Function to render the scatter bubble chart
async function renderScatterBubble() {
  try {
    const start_year = 2000;
    const end_year = 2020;
    const response = await fetch(`http://127.0.0.1:8000/bubble-data/${start_year}/${end_year}`);
    let data = await response.json();

    // Get the container dimensions
    const container = document.getElementById('scatterbubble-container');
    const containerWidth = container.clientWidth;
    
    // Set up chart properties with responsive dimensions
    const width = Math.min(containerWidth, 800);
    const height = width * 0.6;
    const margin = {
      top: 20,
      right: 20,
      bottom: 40,
      left: 50
    };

    // Get interpolated data for current year
    const currentYear = end_year;
    const currentData = dataAt(data, currentYear).filter(d => 
      d.health_exp != null && 
      d.life_exp != null && 
      d.population != null
    );

    // Set up chart properties
    const x = d3.scaleLinear().domain([0, 20]).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([14, 90]).range([height - margin.bottom, margin.top]);
    const radius = d3.scaleSqrt().domain([0, 5e8]).range([0, width / 24]);
    const color = d3.scaleOrdinal(d3.schemeAccent);

    const svg = d3.create("svg").attr("viewBox", [0, 0, width, height]);

    // Create axes and grid
    const xAxis = g => g
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(width / 80, ","))
      .call(g => g.select(".domain").remove())
      .call(g => g.append("text")
        .attr("x", width)
        .attr("y", margin.bottom - 4)
        .attr("fill", "currentColor")
        .attr("text-anchor", "end")
        .text("Current health expenditure (% of GDP) →"));

    const yAxis = g => g
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y))
      .call(g => g.select(".domain").remove())
      .call(g => g.append("text")
        .attr("x", -margin.left)
        .attr("y", 10)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .text("↑ Life expectancy at birth, total (years)"));

    const grid = g => g
      .attr("stroke", "currentColor")
      .attr("stroke-opacity", 0.1)
      .call(g => g.append("g")
        .selectAll("line")
        .data(x.ticks())
        .join("line")
          .attr("x1", d => 0.5 + x(d))
          .attr("x2", d => 0.5 + x(d))
          .attr("y1", margin.top)
          .attr("y2", height - margin.bottom))
      .call(g => g.append("g")
        .selectAll("line")
        .data(y.ticks())
        .join("line")
          .attr("y1", d => 0.5 + y(d))
          .attr("y2", d => 0.5 + y(d))
          .attr("x1", margin.left)
          .attr("x2", width - margin.right));

    svg.append("g").call(xAxis);
    svg.append("g").call(yAxis);
    svg.append("g").call(grid);

    // Create circles for the scatterplot
    const circle = svg.append("g")
      .attr("stroke", "black")
    .selectAll("circle")
    .data(currentData)
    .join("circle")
      .sort((a, b) => d3.descending(a.population, b.population))
      .attr("cx", d => x(d.health_exp))
      .attr("cy", d => y(d.life_exp))
      .attr("r", d => radius(d.population))
      .attr("fill", d => color(d.region))
      .call(circle => circle.append("title")
        .text(d => `${d.name}\n${d.region}`));

    document.getElementById('scatterbubble-container').appendChild(svg.node());
    // animateChart();

  } catch (error) {
    console.error('Error fetching data or rendering chart:', error);
  }
}

// Animate the chart over time with transitions
function animateChart() {
  let currentYear = 2000; // Start year for animation

  function updateData() {
    currentYear++;
    const currentData = dataAt(data, currentYear);
    update(currentData);
  }

  setInterval(updateData, 1000); // Update every second (adjust as needed)
}

window.onload = renderScatterBubble();
