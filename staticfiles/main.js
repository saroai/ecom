const menuIcon = document.querySelector(".menu-icon");
const backdrop = document.querySelector(".backdrop");
const navLinks = document.querySelector(".nav-links");
const closeIcon = document.querySelector(".close-icon");

menuIcon.addEventListener("click", () => {
    backdrop.classList.add("active");
    navLinks.classList.add("active");
});

closeIcon.addEventListener("click", () => {
    backdrop.classList.remove("active");
    navLinks.classList.remove("active");
});

backdrop.addEventListener("click", () => {
    backdrop.classList.remove("active");
    navLinks.classList.remove("active");
});

// added after change

document.addEventListener("DOMContentLoaded", function () {
    let lightboxMainImages = [];
    let lightboxThumbnails = [];

    // Conditionally remove unwanted lightbox view
    if (window.innerWidth >= 768) {
        const lightboxMobile = document.querySelector(".lightbox.mobile");
        if (lightboxMobile) lightboxMobile.remove();

        // Use desktop version
        lightboxMainImages = document.querySelectorAll(".lightbox.pc .main-img img");
        lightboxThumbnails = document.querySelectorAll(".lightbox.pc .thumb-list div");
    } else {
        const lightboxDesktop = document.querySelector(".lightbox.pc");
        if (lightboxDesktop) lightboxDesktop.remove();

        // Use mobile version
        lightboxMainImages = document.querySelectorAll(".lightbox.mobile .main-img img");
        lightboxThumbnails = document.querySelectorAll(".lightbox.mobile .thumb-list div");
    }

    let currentImageIndex = 0;

    function changeImage(index, images, thumbs) {
        images.forEach((img) => img.classList.remove("active"));
        thumbs.forEach((thumb) => thumb.classList.remove("active"));
        images[index].classList.add("active");
        thumbs[index].classList.add("active");
        currentImageIndex = index;
    }

    const iconPrev = document.querySelector(".icon-prev");
    const iconNext = document.querySelector(".icon-next");

    if (iconPrev && iconNext && lightboxMainImages.length > 0) {
        iconPrev.addEventListener("click", () => {
            const newIndex = currentImageIndex <= 0
                ? lightboxMainImages.length - 1
                : currentImageIndex - 1;
            changeImage(newIndex, lightboxMainImages, lightboxThumbnails);
        });

        iconNext.addEventListener("click", () => {
            const newIndex = currentImageIndex >= lightboxMainImages.length - 1
                ? 0
                : currentImageIndex + 1;
            changeImage(newIndex, lightboxMainImages, lightboxThumbnails);
        });
    }
});
