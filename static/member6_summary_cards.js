window.loadFeedbackSummary = async function () {
  const container = document.querySelector("#summary-cards");
  if (!container) return;
  try {
    const response = await fetch("/analytics");
    if (!response.ok) throw new Error("Unable to load summary.");
    const data = await response.json();
    container.replaceChildren();
    const addCard = (label, value) => {
      const card = document.createElement("div");
      card.className = "card";
      const heading = document.createElement("strong");
      heading.textContent = label;
      const number = document.createElement("p");
      number.textContent = value;
      card.append(heading, number);
      container.append(card);
    };
    addCard("Total feedback", data.total_feedback ?? 0);
    Object.entries(data.category_counts || {}).forEach(([category, count]) => addCard(category, count));
  } catch (error) {
    container.textContent = error.message;
  }
};
document.addEventListener("DOMContentLoaded", window.loadFeedbackSummary);
