window.loadFeedbackTable = async function () {
  const container = document.querySelector("#feedback-table");
  if (!container) return;
  try {
    const response = await fetch("/feedback");
    if (!response.ok) throw new Error("Unable to load feedback.");
    const entries = await response.json();
    const table = document.createElement("table");
    const head = document.createElement("thead");
    const headerRow = document.createElement("tr");
    ["Feedback", "Category", "Submitted"].forEach((label) => {
      const th = document.createElement("th");
      th.textContent = label;
      headerRow.append(th);
    });
    head.append(headerRow);
    const body = document.createElement("tbody");
    entries.forEach((entry) => {
      const row = document.createElement("tr");
      [entry.customer_feedback, entry.category, entry.created_at].forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = value ?? "";
        row.append(cell);
      });
      body.append(row);
    });
    table.append(head, body);
    container.replaceChildren(table);
    if (!entries.length) container.textContent = "No feedback has been submitted yet.";
  } catch (error) {
    container.textContent = error.message;
  }
};
document.addEventListener("DOMContentLoaded", window.loadFeedbackTable);
