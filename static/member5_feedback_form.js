const feedbackForm = document.querySelector("#feedback-form");
if (feedbackForm) {
  feedbackForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = document.querySelector("#status");
    const customer_feedback = document.querySelector("#customer_feedback").value.trim();
    const category = document.querySelector("#category").value;
    if (!customer_feedback) {
      status.textContent = "Please enter your feedback.";
      return;
    }
    try {
      const response = await fetch("/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_feedback, category })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Could not save feedback.");
      status.textContent = "Thank you. Your feedback was saved.";
      feedbackForm.reset();
      if (typeof window.loadFeedbackSummary === "function") window.loadFeedbackSummary();
      if (typeof window.loadFeedbackTable === "function") window.loadFeedbackTable();
    } catch (error) {
      status.textContent = error.message;
    }
  });
}
