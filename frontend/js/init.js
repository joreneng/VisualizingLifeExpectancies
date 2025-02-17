const startYear = 1960;
const endYear = 2023;
const years = Array.from({length: endYear - startYear + 1}, (_, i) => startYear + i);

// Wait for DOM content to be loaded
document.addEventListener("DOMContentLoaded", async function() {
    // Setup year filters
    const yearStartSelect = document.getElementById("start-year");
    const yearEndSelect = document.getElementById("end-year");

    // Populate dropdowns
    years.forEach(year => {
        yearStartSelect.add(new Option(year, year));
        yearEndSelect.add(new Option(year, year));
    });

    // Set default values
    yearStartSelect.value = startYear;
    yearEndSelect.value = endYear;

    // Update end year options based on start year selection
    yearStartSelect.addEventListener("change", function() {
        const selectedYear = parseInt(this.value);
        
        // Clear existing options
        yearEndSelect.innerHTML = "";
        
        // Add only years greater than selected start year
        years.filter(year => year > selectedYear)
            .forEach(year => yearEndSelect.add(new Option(year, year)));
        yearEndSelect.value = endYear;
        
        renderAllCharts();
    });

    yearEndSelect.addEventListener("change", renderAllCharts);

    // Function to render all charts
    async function renderAllCharts() {
        try {
            // Always use full range (1960-2023) until user interacts with filters
            const useFilters = yearStartSelect.value !== startYear.toString() || 
                             yearEndSelect.value !== endYear.toString();

            const effectiveStartYear = useFilters ? parseInt(yearStartSelect.value) : startYear;
            const effectiveEndYear = useFilters ? parseInt(yearEndSelect.value) : endYear;

            // Render charts sequentially to avoid race conditions
            console.log("Rendering chloropleth...");
            await renderChloropleth(effectiveStartYear, effectiveEndYear);
            
            console.log("Rendering scatter bubble...");
            await renderScatterBubble(effectiveStartYear, effectiveEndYear);
            
            console.log("Rendering bar chart...");
            await renderBarChart(effectiveStartYear, effectiveEndYear);
            
            console.log("Rendering line chart...");
            await renderLineChart(effectiveStartYear, effectiveEndYear);
            
            console.log("All charts rendered successfully");
        } catch (error) {
            console.error("Error during chart rendering:", error);
        }
    }

    // Initial render
    await renderAllCharts();

    // Handle window resize with debouncing
    window.addEventListener("resize", debounce(async () => {
        console.log("Window resized, re-rendering charts...");
        await renderAllCharts();
    }, 250));
});

// Remove any existing window.onload handlers
window.onload = null; 