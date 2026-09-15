function initMobileMenu() {
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('#menu-principal');

    if (!toggle || !nav) {
        return;
    }

    toggle.addEventListener('click', function () {
        const isOpen = nav.classList.toggle('aberto');
        toggle.setAttribute('aria-expanded', String(isOpen));
        toggle.setAttribute('aria-label', isOpen ? 'Fechar menu' : 'Abrir menu');
    });
}

function initClientsCarousel() {
    const track = document.querySelector('.trilha-clientes');
    const previousButton = document.querySelector('.seta-clientes-esquerda');
    const nextButton = document.querySelector('.seta-clientes-direita');

    if (!track || !previousButton || !nextButton) {
        return;
    }

    // RF: folga em pixels para detectar o início/fim do carrossel
    const SCROLL_END_TOLERANCE = 4;

    function stepSize() {
        const item = track.querySelector('.item-cliente');
        if (!item) {
            return track.clientWidth;
        }

        const styles = window.getComputedStyle(track);
        const gap = Number.parseFloat(styles.columnGap || styles.gap) || 0;
        return item.getBoundingClientRect().width + gap;
    }

    function updateButtons() {
        const maxScroll = track.scrollWidth - track.clientWidth;
        const current = track.scrollLeft;
        const atStart = current <= SCROLL_END_TOLERANCE;
        const atEnd = current >= maxScroll - SCROLL_END_TOLERANCE;

        previousButton.disabled = atStart;
        nextButton.disabled = atEnd;
    }

    previousButton.addEventListener('click', function () {
        track.scrollBy({ left: -stepSize(), behavior: 'smooth' });
    });

    nextButton.addEventListener('click', function () {
        track.scrollBy({ left: stepSize(), behavior: 'smooth' });
    });

    track.addEventListener('scroll', updateButtons);
    window.addEventListener('resize', updateButtons);
    updateButtons();
}

initMobileMenu();
initClientsCarousel();
