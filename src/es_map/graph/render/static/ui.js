export function initSidebar() {
  const settingsBtn = document.getElementById("settings-btn");
  const sidebar = document.getElementById("sidebar");

  settingsBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });

  document.addEventListener("click", (event) => {
    if (!sidebar.contains(event.target) && event.target !== settingsBtn) {
      sidebar.classList.remove("open");
    }
  });
}
