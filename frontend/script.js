document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.querySelector('.hamburger');
    const navList = document.querySelector('.nav-list');
    const nav = document.querySelector('.nav');

    const closeNavMenu = () => {
        if (navList.classList.contains('active')) {
            navList.classList.remove('active');
        }
    };

    hamburger.addEventListener('click', () => {
        navList.classList.toggle('active');
    });

    navList.addEventListener('click', (event) => {
        if (event.target.tagName === 'A') {
            closeNavMenu();

            const targetId = event.target.hash;
            if (targetId) {
                event.preventDefault();

                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    const navHeight = nav.offsetHeight;
                    const buffer = 20;

                    window.scrollTo({
                        top: targetElement.offsetTop - navHeight - buffer,
                        behavior: 'smooth'
                    });
                }
            }
        }
    });

    document.addEventListener('click', (event) => {
        if (!nav.contains(event.target) && navList.classList.contains('active')) {
            closeNavMenu();
        }
    });

    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth > 768) {
                closeNavMenu();
            }
        }, 250);
    });
});