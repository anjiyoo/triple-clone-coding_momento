const IMAGE_WIDTH = 640;

document.addEventListener('DOMContentLoaded', (event) => {
    const slideshows = document.querySelectorAll(".slideshow-container");

    slideshows.forEach((slideshow) => {
        const slides = slideshow.querySelector(".slides");
        const prevBtn = slideshow.querySelector(".prev");
        const nextBtn = slideshow.querySelector(".next");
        const totalSlides = slideshow.querySelectorAll(".slides .slide").length;
        let curPos = 0;

        function updateButtons() {
            if (curPos === 0) {
                prevBtn.classList.add("disabled");
            } else {
                prevBtn.classList.remove("disabled");
            }

            if (curPos === totalSlides - 1) {
                nextBtn.classList.add("disabled");
            } else {
                nextBtn.classList.remove("disabled");
            }
        }

        function prevSlide() {
            if (curPos > 0) {
                curPos--;
                slides.style.transform = `translateX(-${curPos * IMAGE_WIDTH}px)`;
            }
            updateButtons();
        }

        function nextSlide() {
            if (curPos < totalSlides - 1) {
                curPos++;
                slides.style.transform = `translateX(-${curPos * IMAGE_WIDTH}px)`;
            }
            updateButtons();
        }

        prevBtn.addEventListener('click', prevSlide);
        nextBtn.addEventListener('click', nextSlide);

        updateButtons();
    });
});

function navigateToGuide(guideNumber) {
    let url = '';
    switch (guideNumber) {
        case 1:
            url = '/guidepage/guide_plan';
            break;
        case 2:
            url = '/guidepage/guide_info';
            break;
        case 3:
            url = '/guidepage/guide_reservation';
            break;
        default:
            url = '/';
            break;
    }
    window.location.href = url;
}