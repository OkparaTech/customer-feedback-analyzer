async function loadKeywordChart() {
  const list = document.querySelector("#keyword-list");
  if (!list) return;
  try {
    const response = await fetch("/analytics");
    if (!response.ok) throw new Error("Unable to load keywords.");
    const data = await response.json();
    list.replaceChildren();
    (data.top_keywords || []).forEach(({ word, count }) => {
      const item = document.createElement("li");
      item.textContent = `${word}: ${count}`;
      list.append(item);
    });
    if (!list.children.length) list.textContent = "No keywords yet.";
  } catch (error) {
    list.textContent = error.message;
  }
}
document.addEventListener("DOMContentLoaded", loadKeywordChart);
