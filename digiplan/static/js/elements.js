export const statusquoDropdown = document.getElementById("situation_today");
export const futureDropdown = document.getElementById("result_views");
export const resultsTabs = document.getElementById("results-tabs");

const carouselEl = document.getElementById('carouselExampleIndicators');

// Show onboarding modal on start
document.addEventListener('DOMContentLoaded', (event) => {
  let myModal = new bootstrap.Modal(document.getElementById('onboardingModal'), {});
  myModal.show();
});

// Prevent continuous cycle of modal carousel
document.addEventListener("DOMContentLoaded", function() {
  let carousel = new bootstrap.Carousel(carouselEl, {
    wrap: false
  });

  let prevButton = document.querySelector('.carousel-control-prev');
  let nextButton = document.querySelector('.carousel-control-next');

  prevButton.addEventListener('click', function (event) {
    event.preventDefault();
    carousel.prev();
  });

  nextButton.addEventListener('click', function (event) {
    event.preventDefault();
    carousel.next();
  });

  // Add .transparent class to nav buttons
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

// Add .active class to current carousel indicator
carouselEl.addEventListener('slide.bs.carousel', function(event) {
  const indicators = document.querySelectorAll('.carousel-indicators button');

  indicators.forEach(function(indicator) {
    indicator.classList.remove('active');
  });
  
  indicators[event.to].classList.add('active');
});