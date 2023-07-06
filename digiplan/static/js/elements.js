export const statusquoDropdown = document.getElementById("situation_today");
export const resultsTabs = document.getElementById("results-tabs");

// Onboarding modal
document.addEventListener('DOMContentLoaded', (event) => {
    var myModal = new bootstrap.Modal(document.getElementById('onboardingModal'), {});
    myModal.show();
});