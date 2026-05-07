(function () {
  const buttonId = "job-portal-save-button";
  if (document.getElementById(buttonId)) return;

  const button = document.createElement("button");
  button.id = buttonId;
  button.textContent = "Save to Portal";
  button.style.position = "fixed";
  button.style.right = "20px";
  button.style.bottom = "20px";
  button.style.zIndex = "2147483647";
  button.style.padding = "10px 14px";
  button.style.border = "0";
  button.style.borderRadius = "6px";
  button.style.background = "#18201d";
  button.style.color = "#fff";
  button.style.font = "600 14px system-ui, sans-serif";
  button.style.boxShadow = "0 10px 30px rgba(0, 0, 0, 0.18)";

  button.addEventListener("click", async () => {
    const title =
      document.querySelector("h1")?.textContent?.trim() ||
      document.querySelector("[data-testid='jobsearch-JobInfoHeader-title']")?.textContent?.trim() ||
      document.title;
    const company =
      document.querySelector("[data-company-name]")?.textContent?.trim() ||
      document.querySelector(".job-details-jobs-unified-top-card__company-name")?.textContent?.trim() ||
      document.querySelector("[data-testid='inlineHeader-companyName']")?.textContent?.trim() ||
      null;
    const description =
      document.querySelector(".jobs-description-content__text")?.textContent?.trim() ||
      document.querySelector("#jobDescriptionText")?.textContent?.trim() ||
      document.body.innerText.slice(0, 6000);

    chrome.runtime.sendMessage({
      type: "SAVE_JOB",
      payload: {
        url: window.location.href,
        title,
        company,
        description,
        source: window.location.hostname
      }
    });
  });

  document.body.appendChild(button);
})();
