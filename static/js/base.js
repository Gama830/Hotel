// Base Template JavaScript

// Mobile Navigation Toggle
function toggleMobileNav() {
  const navbar = document.getElementById("leftNavbar");
  navbar.classList.toggle("mobile-open");
}

// Show mobile toggle on small screens
function checkScreenSize() {
  const mobileToggle = document.querySelector(".mobile-toggle");
  if (window.innerWidth <= 768) {
    mobileToggle.style.display = "block";
  } else {
    mobileToggle.style.display = "none";
    document.getElementById("leftNavbar").classList.remove("mobile-open");
  }
}

// Dropdown functionality
function toggleDropdown(dropdownId) {
  const dropdown = document.getElementById(dropdownId);
  const allDropdowns = document.querySelectorAll('.nav-dropdown');

  // Close all other dropdowns
  allDropdowns.forEach(dd => {
    if (dd.id !== dropdownId) {
      dd.classList.remove('open');
    }
  });

  // Toggle current dropdown
  dropdown.classList.toggle('open');
}

// Initialize base functionality
document.addEventListener('DOMContentLoaded', function() {
  // Check screen size on load and resize
  window.addEventListener("resize", checkScreenSize);
  window.addEventListener("load", checkScreenSize);

  // Close mobile nav when clicking outside
  document.addEventListener("click", function (event) {
    const navbar = document.getElementById("leftNavbar");
    const toggle = document.querySelector(".mobile-toggle");

    if (
      window.innerWidth <= 768 &&
      navbar && toggle &&
      !navbar.contains(event.target) &&
      !toggle.contains(event.target)
    ) {
      navbar.classList.remove("mobile-open");
    }
  });

  // Close dropdowns when clicking outside
  document.addEventListener('click', function (event) {
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    const clickedInsideDropdown = event.target.closest('.nav-dropdown');

    if (!clickedInsideDropdown) {
      dropdowns.forEach(dropdown => {
        dropdown.classList.remove('open');
      });
    }
  });
});