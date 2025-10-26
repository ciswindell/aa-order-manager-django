// Dark mode toggle functionality with localStorage persistence

// Get stored theme preference or default to light
function getStoredTheme() {
    return localStorage.getItem('theme') || 'light';
}

// Store theme preference
function setStoredTheme(theme) {
    localStorage.setItem('theme', theme);
}

// Apply theme to document
function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    
    // Update toggle button state if it exists
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
        toggle.checked = (theme === 'dark');
    }
}

// Toggle between light and dark themes
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    setStoredTheme(newTheme);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const storedTheme = getStoredTheme();
    setTheme(storedTheme);
    
    // Attach event listener to toggle
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
        toggle.addEventListener('change', toggleTheme);
    }
});

