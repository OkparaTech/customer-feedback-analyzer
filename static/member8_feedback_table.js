window.showAllFeedback = false;
window.loadFeedbackTable = async function () {
  const container = document.querySelector("#feedback-table");
  if (!container) return;
  try {
    const response = await fetch("/feedback");
    if (!response.ok) throw new Error("Unable to load feedback.");
    const entries = await response.json();
    if (!entries.length) { container.textContent = "No feedback has been submitted yet."; return; }
    const shown = window.showAllFeedback ? entries : entries.slice(0, 5);
    const table = document.createElement("table");
    const headerRow = document.createElement("tr");
    ["#", "Feedback", "Category", "Sentiment", "Date"].forEach((label) => {
      const th = document.createElement("th");
      th.textContent = label;
      headerRow.append(th);
    });
    const head = document.createElement("thead");
    head.append(headerRow);
    const body = document.createElement("tbody");
    shown.forEach((entry, index) => {
      const row = document.createElement("tr");
      const sentiment = entry.sentiment || "Neutral";
      [index + 1, entry.customer_feedback, entry.category, sentiment, (entry.created_at || "").slice(0, 10)].forEach((value, col) => {
        const cell = document.createElement("td");
        if (col === 3) {
          const badge = document.createElement("span");
          badge.className = `badge b-${value}`;
          badge.textContent = value;
          cell.append(badge);
        } else {
          cell.textContent = value ?? "";
        }
        row.append(cell);
      });
      body.append(row);
    });
    table.append(head, body);
    const footer = document.createElement("p");
    footer.className = "muted";
    footer.textContent = `Showing ${shown.length} of ${entries.length} feedbacks `;
    if (entries.length > 5) {
      const toggle = document.createElement("button");
      toggle.type = "button"; toggle.className = "link";
      toggle.textContent = window.showAllFeedback ? "Show less" : "View all feedback →";
      toggle.addEventListener("click", () => { window.showAllFeedback = !window.showAllFeedback; window.loadFeedbackTable(); });
      footer.append(toggle);
    }
    container.replaceChildren(table, footer);
  } catch (error) {
    container.textContent = error.message;
  }
};
document.addEventListener("DOMContentLoaded", window.loadFeedbackTable);