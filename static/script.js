
const hamburgerBtn = document.getElementById('hamburger-btn');
const sidebar = document.querySelector('.sidebar');
const mainContent = document.querySelector('.main-content');

hamburgerBtn.addEventListener('click', () => {
const expanded = hamburgerBtn.getAttribute('aria-expanded') === 'true';
hamburgerBtn.setAttribute('aria-expanded', !expanded);
sidebar.classList.toggle('open');
document.body.classList.toggle('menu-open');
mainContent.classList.toggle('menu-active');
});

// Optional: Close sidebar if user clicks outside sidebar on small screen
mainContent.addEventListener('click', () => {
if (sidebar.classList.contains('open')) {
sidebar.classList.remove('open');
document.body.classList.remove('menu-open');
mainContent.classList.remove('menu-active');
hamburgerBtn.setAttribute('aria-expanded', false);
}
});

