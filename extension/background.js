chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== "SAVE_JOB") return false;

  fetch("http://localhost:8000/api/jobs/capture-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(message.payload)
  })
    .then(async (response) => {
      if (!response.ok) throw new Error(await response.text());
      return response.json();
    })
    .then((job) => sendResponse({ ok: true, job }))
    .catch((error) => sendResponse({ ok: false, error: String(error) }));

  return true;
});
