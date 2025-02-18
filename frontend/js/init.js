const start_year = 1960;
const end_year = 2023;
const years = Array.from({length: end_year - start_year}, (_, i) => start_year + 1 + i);

// Wait for DOM content to be loaded
document.addEventListener("DOMContentLoaded", async function () {
    // Setup year filters
    const yearStartSelect = document.getElementById("start-year");
    const yearEndSelect = document.getElementById("end-year");

    yearStartSelect.add(new Option(start_year, start_year));

    // Populate dropdowns
    years.forEach(year => {
        yearStartSelect.add(new Option(year, year));
        yearEndSelect.add(new Option(year, year));
    });

    // Set default values
    yearStartSelect.value = start_year;
    yearEndSelect.value = end_year;

    // Update end year options based on start year selection
    yearStartSelect.addEventListener("change", function () {
        const selectedYear = parseInt(this.value);

        // Clear existing options
        yearEndSelect.innerHTML = "";

        // Add only years greater than selected start year
        years.filter(year => year > selectedYear)
            .forEach(year => yearEndSelect.add(new Option(year, year)));
        yearEndSelect.value = end_year;

        renderAllCharts();
    });

    yearEndSelect.addEventListener("change", renderAllCharts);

    // Function to render all charts
    async function renderAllCharts() {
        try {
            // Always use full range (1960-2023) until user interacts with filters
            const useFilters = yearStartSelect.value !== start_year ||
                yearEndSelect.value !== end_year;

            const effectiveStartYear = useFilters ? parseInt(yearStartSelect.value) : start_year;
            const effectiveEndYear = useFilters ? parseInt(yearEndSelect.value) : end_year;

            // Render charts sequentially to avoid race conditions
            await renderChloropleth(effectiveStartYear, effectiveEndYear);

            await renderScatterBubble(effectiveStartYear, effectiveEndYear);

            await renderBarChart(effectiveStartYear, effectiveEndYear);

            await renderLineChart(effectiveStartYear, effectiveEndYear);
        } catch (error) {
            console.error("Error during chart rendering:", error);
        }
    }

    // Initial render
    await renderAllCharts();

    // Handle window resize with debouncing
    window.addEventListener("resize", debounce(async () => {
        await renderAllCharts();
    }, 250));
});

// Remove any existing window.onload handlers
window.onload = null; 