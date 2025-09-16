// Test date formatting to verify consistency
const dateString = "2024-01-15";

// Original problematic approach
const date1 = new Date(dateString);
console.log("toLocaleDateString():", date1.toLocaleDateString());

// Fixed approach using UTC
const date2 = new Date(dateString);
const month = String(date2.getUTCMonth() + 1).padStart(2, '0');
const day = String(date2.getUTCDate()).padStart(2, '0');
const year = date2.getUTCFullYear();
const formatted = `${month}/${day}/${year}`;
console.log("UTC formatted:", formatted);

// Test with different dates
const testDates = ["2024-01-14", "2024-01-15", "2024-12-31"];
testDates.forEach(d => {
    const date = new Date(d);
    const m = String(date.getUTCMonth() + 1).padStart(2, '0');
    const dy = String(date.getUTCDate()).padStart(2, '0');
    const y = date.getUTCFullYear();
    console.log(`${d} -> ${m}/${dy}/${y}`);
});