export const statusquoDropdown = document.getElementById("situation_today");
export const resultsTabs = document.getElementById("results-tabs");

// Show onboarding modal on start
document.addEventListener('DOMContentLoaded', (event) => {
    var myModal = new bootstrap.Modal(document.getElementById('onboardingModal'), {});
    myModal.show();
});

// Prevent continuous cycle of modal carousel
document.addEventListener("DOMContentLoaded", function() {
    var carouselEl = document.querySelector('#carouselExampleIndicators');
    var carousel = new bootstrap.Carousel(carouselEl, {
      wrap: false
    });

    var prevButton = document.querySelector('.carousel-control-prev');
    var nextButton = document.querySelector('.carousel-control-next');

    prevButton.addEventListener('click', function (event) {
      event.preventDefault();
      carousel.prev();
    });

    nextButton.addEventListener('click', function (event) {
      event.preventDefault();
      carousel.next();
    });

    carouselEl.addEventListener('slid.bs.carousel', function () {
      const carouselItems = carouselEl.querySelectorAll('.carousel-item');
      const currentIndex = Array.prototype.indexOf.call(carouselItems, carouselEl.querySelector('.carousel-item.active'));
      if (currentIndex === 0) {
        prevButton.classList.add('transparent');
      } else {
        prevButton.classList.remove('transparent');
      }

      if (currentIndex === carouselItems.length - 1) {
        nextButton.classList.add('transparent');
      } else {
        nextButton.classList.remove('transparent');
      }
    });
  });
