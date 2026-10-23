function drawTrend(box, days) {
  if (!box || !days.length) return;
  const W = 320, H = 150, pad = 24;
  const max = Math.max(5, ...days.map((d) => d.count));
  const x = (i) => pad + (i * (W - 2 * pad)) / Math.max(1, days.length - 1);
  const y = (c) => H - pad - (c * (H - 2 * pad)) / max;
  const pts = days.map((d, i) => `${x(i)},${y(d.count)}`).join(" ");
  const dots = days.map((d, i) => `<circle cx="${x(i)}" cy="${y(d.count)}" r="3.5" fill="#2563eb"/>`).join("");
  const labels = days.map((d, i) => `<text x="${x(i)}" y="${H - 6}" font-size="9" text-anchor="middle" fill="#6b7794">${d.date.slice(5)}</text>`).join("");
  box.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%"><polygon points="${x(0)},${H - pad} ${pts} ${x(days.length - 1)},${H - pad}" fill="#2563eb22"/><polyline points="${pts}" fill="none" stroke="#2563eb" stroke-width="2"/>${dots}${labels}</svg>`;
}

window.loadFeedbackSummary = async function () {
  const cards = document.querySelector("#summary-cards");
  if (!cards) return;
  try {
    const response = await fetch("/analytics");
    if (!response.ok) throw new Error("Unable to load summary.");
    const data = await response.json();
    const el = (tag, cls, text) => {
      const node = document.createElement(tag);
      if (cls) node.className = cls;
      if (text !== undefined) node.textContent = text;
      return node;
    };
    const addCard = (icon, cls, label, value, note) => {
      const body = el("div");
      body.append(el("div", "", label), el("div", "num", value), el("small", "", note));
      const card = el("div", "card");
      card.append(el("div", "icon " + cls, icon), body);
      cards.append(card);
    };
    cards.replaceChildren();
    const recent = data.recent_activity || {};
    const change = recent.change_percent;
    addCard("💬", "c-total", "Total Feedback", data.total_feedback ?? 0,
      change == null ? `${recent.last_7_days ?? 0} in last 7 days`
        : `${change >= 0 ? "▲" : "▼"} ${Math.abs(change)}% vs previous 7 days`);
    const counts = data.sentiment_counts || {}, pcts = data.sentiment_percentages || {};
    [["😊", "c-pos", "Positive"], ["😐", "c-neu", "Neutral"], ["😞", "c-neg", "Negative"]].forEach(
      ([icon, cls, name]) => addCard(icon, cls, name, `${pcts[name] ?? 0}%`, `${counts[name] ?? 0} feedbacks`));
    addCard("💡", "c-feat", "Feature Requests", `${(data.category_percentages || {})["Feature Request"] ?? 0}%`,
      `${(data.category_counts || {})["Feature Request"] ?? 0} feedbacks`);
    drawTrend(document.querySelector("#trend-chart"), recent.daily_counts || []);
  } catch (error) {
    cards.textContent = error.message;
  }
};
document.addEventListener("DOMContentLoaded", window.loadFeedbackSummary);