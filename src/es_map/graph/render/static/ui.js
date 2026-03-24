export function initSidebar({ sidebarId, triggerId }) {
  const sidebar = document.getElementById(sidebarId);
  const trigger = document.getElementById(triggerId);

  function open() {
    sidebar.classList.add("open");
  }

  function close() {
    sidebar.classList.remove("open");
  }

  function toggle() {
    sidebar.classList.toggle("open");
  }

  trigger?.addEventListener("click", (event) => {
    event.stopPropagation();
    toggle();
  });

  document.addEventListener("click", (event) => {
    if (!sidebar.contains(event.target) && event.target !== trigger) {
      close();
    }
  });

  return { open, close, toggle };
}

export function updateHostSidebar(nodeData) {
  document.getElementById("host-hostname").textContent = nodeData.label;
  document.getElementById("host-id").textContent = nodeData.id;
  document.getElementById("host-ips").textContent = nodeData.ip_addresses;
  document.getElementById("host-subnets").textContent = nodeData.subnets;
}
