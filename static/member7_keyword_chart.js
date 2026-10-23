function drawDonut(box, data) {
  const colors = ["#2563eb", "#22a06b", "#f5b800", "#f08a24", "#8b5cf6", "#ef4444", "#64748b"];
  const entries = Object.entries(data.category_counts || {}).filter(([, n]) => n > 0);
  const total = entries.reduce((sum, [, n]) => sum + n, 0);
  box.replaceChildren();
  if (!total) { box.textContent = "No data yet."; return; }
  let acc = 0;
  const stops = entries.map(([, n], i) => {
    const start = acc; acc += (n / total) * 100;
    return `${colors[i % colors.length]} ${start}% ${acc}%`;
  });
  const donut = document.createElement("div");
  donut.className = "donut";
  donut.style.background = `conic-gradient(${stops.join(",")})`;
  const center = document.createElement("div");
  center.className = "donut-center";
  center.textContent = `${total} Total`;
  donut.append(center);
  const legend = document.createElement("div");
  legend.className = "legend";
  entries.forEach(([name, n], i) => {
    const row = document.createElement("div");
    const dot = document.createElement("span");
    dot.className = "dot";
    dot.style.background = colors[i % colors.length];
    row.append(dot, `${name} ${(data.category_percentages || {})[name] ?? Math.round((n / total) * 100)}%`);
    legend.append(row);
  });
  box.append(donut, legend);
}

window.loadKeywordChart = async function () {
  const list = document.querySelector("#keyword-list");
  if (!list) return;
  try {
    const response = await fetch("/analytics");
    if (!response.ok) throw new Error("Unable to load keywords.");
    const data = await response.json();
    const keywords = (data.top_keywords || []).slice(0, 5);
    const max = Math.max(1, ...keywords.map((k) => k.count));
    list.replaceChildren();
    keywords.forEach(({ word, count }) => {
      const row = document.createElement("div");
      row.className = "kw-row";
      const label = document.createElement("span");
      label.className = "kw-word"; label.textContent = word;
      const track = document.createElement("div");
      track.className = "kw-track";
      const fill = document.createElement("span");
      fill.style.width = `${(count / max) * 100}%`;
      track.append(fill);
      const num = document.createElement("span");
      num.className = "kw-count"; num.textContent = count;
      row.append(label, track, num);
      list.append(row);
    });
    if (!keywords.length) list.textContent = "No keywords yet.";
    const donut = document.querySelector("#category-chart");
    if (donut) drawDonut(donut, data);
  } catch (error) {
    list.textContent = error.message;
  }
};
document.addEventListener("DOMContentLoaded", window.loadKeywordChart);