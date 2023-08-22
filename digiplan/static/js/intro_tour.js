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
    text: 'Schritt für Schritt zu Ihrem eigenen Szenario.',
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
    id: 'start'
});

tour.addStep({
    title: 'Situation heute',
    text: 'Schauen Sie sich die Situation heute an. Wählen Sie eine Kategorie aus.',
    attachTo: {
        element: '#situation_today',
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
    title: 'Situation heute',
    text: 'Zu jeder Kategorie gibt es ein Diagramm.',
    attachTo: {
        element: '#region_chart_statusquo',
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
    id: 'region_chart'
});


tour.addStep({
    title: 'Karte',
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
                return this.next();
            },
            classes: 'shepherd-button-primary',
            text: 'Weiter'
        }
    ],
    id: 'layer_switch'
});


tour.addStep({
    title: 'Karte',
    text: 'Klicken Sie auf ein einzelnes Icon, um mehr über dieses Kraftwerk etc. zu erfahren.',
    attachTo: {
        element: '.maplibregl-canvas',
        on: 'top'
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
    id: 'cluster_popup'
});


tour.addStep({
    title: 'Nächster Schritt',
    text: 'Hier gehts weiter zu den Einstellungen.',
    attachTo: {
        element: '#menu_next_btn',
        on: 'bottom'
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
    title: 'Einstellungen',
    text: 'Schauen Sie, wie sich die Verteilung verändert.',
    attachTo: {
        element: '.power-mix__chart',
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
    id: 'power_mix_chart'
});


tour.addStep({
    title: 'Einstellungen',
    text: 'Wechseln Sie zu den Einstellungen für Wärme und Infrastruktur.',
    attachTo: {
        element: '#settings_area_tab',
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
    id: 'settings_area_tab'
});


tour.addStep({
    title: 'Nächster Schritt',
    text: 'Hier gehts weiter zu den Ergebnissen und Sie starten auch gleich die Simulierung ihres Szenarios.',
    attachTo: {
        element: '#menu_next_btn',
        on: 'bottom'
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
    id: 'menu_next_btn2'
});

tour.addStep({
    title: 'Ergebnisse',
    text: 'Schauen Sie sich die Ergebnisse der Simulation auf der Karte an. Wählen Sie eine Kategorie aus.',
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
                return this.next();
            },
            classes: 'shepherd-button-primary',
            text: 'Weiter'
        }
    ],
    id: 'results_on_map'
});


tour.addStep({
    title: 'Ergebnisse',
    text: 'Wählen Sie auf der Karte eine Region aus und schauen Sie sich die detailierten Informationen in einem Diagramm an.',
    attachTo: {
        element: '.maplibregl-canvas',
        on: 'top'
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
    id: 'popups'
});


tour.addStep({
    title: 'Einstellungen',
    text: 'Wechseln Sie zwischen der Karten- und der Diagramm-Ansicht, sobald die Simulation abgeschlossen ist.',
    attachTo: {
        element: '#myTab',
        on: 'bottom'
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
                document.getElementById("chart_view_tab").click();
                return this.next();
            },
            classes: 'shepherd-button-primary',
            text: 'Weiter'
        }
    ],
    id: 'chart_view_tab'
});


tour.addStep({
    title: 'Fertig',
    text: 'Viel Spaß mit dem Tool :D.',
    attachTo: {
        element: '#chart_view_tab',
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
    id: 'end'
});


onbaordingCloseBtn.addEventListener("click", function() {
  tour.start();
});
