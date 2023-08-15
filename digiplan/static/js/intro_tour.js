const onbaordingCloseBtn = document.getElementById("close-onboarding");

const tour = new Shepherd.Tour({  // jshint ignore:line
    useModalOverlay: true,
    defaultStepOptions: {
        cancelIcon: {
            enabled: true
        },
        classes: 'class-1 class-2',
        scrollTo: {behavior: 'smooth', block: 'center'}
    }
});


tour.addStep({
    title: 'Navigation',
    text: 'Schritt für Schritt zu Ihrem eigenen Szenario',
    attachTo: {
        element: '.steps',
        on: 'bottom'
    },
    buttons: [
        {
            action() {
                return this.cancel();
            },
            classes: 'shepherd-button-secondary',
            text: 'Tour beenden'
        },
        {
            action() {
                return this.next();
            },
            text: 'Weiter'
        }

    ],
    id: 'creating'
});

tour.addStep({
    title: 'Einstellungen',
    text: 'Schauen Sie sich die Situation heute an.',
    attachTo: {
        element: '#panel_1_today',
        on: 'right'
    },
    buttons: [
        {
            action() {
                return this.back();
            },
            classes: 'shepherd-button-secondary',
            text: 'Zurück'
        },
        {
            action() {
                return this.next();
            },
            classes: 'shepherd-button-primary',
            text: 'Weiter'
        }
    ],
    id: 'situation_today'
});

tour.addStep({
    title: 'Einstellungen',
    text: 'Lassen Sie sich die unterschiedlichen Anlagentypen auf der Karte anzeigen.',
    attachTo: {
        element: '#js-map-layers-box',
        on: 'left'
    },
    buttons: [
        {
            action() {
                return this.back();
            },
            classes: 'shepherd-button-secondary',
            text: 'Zurück'
        },
        {
            action() {
                document.getElementById("menu_next_btn").click();
                return this.next();
            },
            classes: 'shepherd-button-primary',
            text: 'Weiter'
        }
    ],
    id: 'layer_switch'
});


tour.addStep({
    title: 'Nächster Schritt',
    text: 'Hier gehts weiter. Klicken Sie, um zum nächsten Schritt zu kommen.',
    attachTo: {
        element: '#menu_next_btn',
        on: 'bottom'
    },advanceOn: {
        selector: '#menu_next_btn',
        event: 'click'
    },
    buttons: [
        {
            action() {
                return this.back();
            },
            classes: 'shepherd-button-secondary',
            text: 'Zurück'
        }
    ],
    id: 'menu_next_btn'
});

tour.addStep({
    title: 'Einstellungen',
    text: 'Verändern Sie die Einstellungen, um Ihr eigenes Szenario zu erstellen.',
    attachTo: {
        element: '#panel_2_settings',
        on: 'right'
    },
    buttons: [
        {
            action() {
                return this.back();
            },
            classes: 'shepherd-button-secondary',
            text: 'Zurück'
        },
        {
            action() {
                return this.next();
            },
            classes: 'shepherd-button-primary',
            text: 'Weiter'
        }
    ],
    id: 'panel_1_today'
});

tour.addStep({
    title: 'Einstellungen',
    text: 'Hier können Sie mehr ins Detail gehen.',
    attachTo: {
        element: '.c-slider__label--more',
        on: 'right'
    },
    buttons: [
        {
            action() {
                return this.back();
            },
            classes: 'shepherd-button-secondary',
            text: 'Zurück'
        },
        {
            action() {
                return this.next();
            },
            classes: 'shepherd-button-primary',
            text: 'Weiter'
        }
    ],
    id: 'more_slider'
});

tour.addStep({
    title: 'Nächster Schritt',
    text: 'Hier gehts weiter. Klicken Sie, um zum nächsten Schritt zu kommen.',
    attachTo: {
        element: '#menu_next_btn',
        on: 'bottom'
    },advanceOn: {
        selector: '#menu_next_btn',
        event: 'click'
    },
    buttons: [
        {
            action() {
                return this.back();
            },
            classes: 'shepherd-button-secondary',
            text: 'Zurück'
        }
    ],
    id: 'menu_next_btn2'
});

tour.addStep({
    title: 'Einstellungen',
    text: 'Schauen Sie sich verschiedene Daten an.',
    attachTo: {
        element: '#panel_3_results',
        on: 'right'
    },
    buttons: [
        {
            action() {
                return this.back();
            },
            classes: 'shepherd-button-secondary',
            text: 'Zurück'
        },
        {
            action() {
                return this.complete();
            },
            classes: 'shepherd-button-primary',
            text: 'Fertig'
        }
    ],
    id: 'results'
});

onbaordingCloseBtn.addEventListener("click", function() {
  tour.start();
});
