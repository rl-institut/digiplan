"""Base settings to build other settings files upon."""
import logging
import os
import sys

import environ
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_mapengine import setup

ROOT_DIR = environ.Path(__file__) - 3  # (digiplan/config/settings/base.py - 3 = digiplan/)
APPS_DIR = ROOT_DIR.path("digiplan")
DATA_DIR = APPS_DIR.path("data")
DIGIPIPE_DIR = DATA_DIR.path("digipipe")
DIGIPIPE_GEODATA_DIR = DIGIPIPE_DIR.path("geodata")
METADATA_DIR = APPS_DIR.path("metadata")

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "UTC"
# https://docs.djangoproject.com/en/dev/ref/settings/#languages
LANGUAGES = (
    ("en", _("English")),
    ("de", _("German")),
)
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
# 'de' is the standard language
LANGUAGE_CODE = "de"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [ROOT_DIR.path("locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    POSTGRES_USER = env.str("POSTGRES_USER")
    POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
    POSTGRES_HOST = env.str("POSTGRES_HOST")
    POSTGRES_PORT = env.str("POSTGRES_PORT")
    POSTGRES_DB = env.str("POSTGRES_DB")
    DATABASE_URL = f"postgis://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    os.environ["DATABASE_URL"] = DATABASE_URL
    DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.forms",
]

THIRD_PARTY_APPS = [
    "foundation_formtags",  # Form layouts
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_distill",
]

LOCAL_APPS = ["digiplan.map.apps.MapConfig", "django_oemof", "django_mapengine"]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "digiplan.contrib.sites.migrations"}

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR.path("static"))]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("data"))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": ["django.template.loaders.filesystem.Loader", "django.template.loaders.app_directories.Loader"],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "digiplan.utils.context_processors.settings_context",
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Hendrik Huyskens""", "hendrik.huyskens@rl-institut.de")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s",  # noqa: ISC001
        },
    },
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "verbose"}},
    "root": {"level": "INFO", "handlers": ["console"]},
}


# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/quickstart/#installation
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]

# django-libsass
# ------------------------------------------------------------------------------
COMPRESS_PRECOMPILERS = [("text/x-scss", "django_libsass.SassCompiler")]

COMPRESS_CACHEABLE_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

# celery
# ------------------------------------------------------------------------------
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# test
TESTING = "test" in sys.argv[1:]
if TESTING:
    logging.info("In TEST Mode - Disableling Migrations")

    class DisableMigrations:
        """Disables migrations for test mode."""

        def __contains__(self, item) -> bool:  # noqa: D105, ANN001
            return True

        def __getitem__(self, item):  # noqa: D105, ANN001, ANN204
            return None

    MIGRATION_MODULES = DisableMigrations()

# Your stuff...
# ------------------------------------------------------------------------------
PASSWORD_PROTECTION = env.bool("PASSWORD_PROTECTION", False)
PASSWORD = env.str("PASSWORD", default=None)
if PASSWORD_PROTECTION and PASSWORD is None:
    msg = "Password protection is on, but no password is given"
    raise ValidationError(msg)

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

OEMOF_SCENARIO = env.str("OEMOF_SCENARIO", "scenario_2045")

# django-mapengine
# ------------------------------------------------------------------------------
MAP_ENGINE_CENTER_AT_STARTUP = [12.537917858911896, 51.80812518969171]
MAP_ENGINE_ZOOM_AT_STARTUP = 9
MAP_ENGINE_MAX_BOUNDS = [[11.280733017118229, 51.22918643452503], [13.616574868700604, 52.35515806663738]]

MAP_ENGINE_IMAGES = [
    setup.MapImage("wind", "images/icons/map_wind.png"),
    setup.MapImage("pv", "images/icons/map_pv.png"),
    setup.MapImage("hydro", "images/icons/map_hydro.png"),
    setup.MapImage("biomass", "images/icons/map_biomass.png"),
    setup.MapImage("combustion", "images/icons/map_combustion.png"),
    setup.MapImage("gsgk", "images/icons/map_gsgk.png"),
    setup.MapImage("storage", "images/icons/map_battery.png"),
]

MAP_ENGINE_API_MVTS = {
    "municipality": [
        setup.MVTAPI("municipality", "map", "Municipality"),
        setup.MVTAPI("municipalitylabel", "map", "Municipality", "label_tiles"),
    ],
    "static": [
        setup.MVTAPI("soil_quality_low", "map", "SoilQualityLow"),
        setup.MVTAPI("soil_quality_high", "map", "SoilQualityHigh"),
        setup.MVTAPI("landscape_protection_area", "map", "LandscapeProtectionArea"),
        setup.MVTAPI("forest", "map", "Forest"),
        setup.MVTAPI("special_protection_area", "map", "SpecialProtectionArea"),
        setup.MVTAPI("air_traffic", "map", "AirTraffic"),
        setup.MVTAPI("aviation", "map", "Aviation"),
        setup.MVTAPI("biosphere_reserve", "map", "BiosphereReserve"),
        setup.MVTAPI("drinking_water_protection_area", "map", "DrinkingWaterArea"),
        setup.MVTAPI("fauna_flora_habitat", "map", "FaunaFloraHabitat"),
        setup.MVTAPI("floodplain", "map", "Floodplain"),
        setup.MVTAPI("grid", "map", "Grid"),
        setup.MVTAPI("industry", "map", "Industry"),
        setup.MVTAPI("less_favoured_areas_agricultural", "map", "LessFavouredAreasAgricultural"),
        setup.MVTAPI("military", "map", "Military"),
        setup.MVTAPI("nature_conservation_area", "map", "NatureConservationArea"),
        setup.MVTAPI("railway", "map", "Railway"),
        setup.MVTAPI("road_default", "map", "Road"),
        setup.MVTAPI("road_railway-500m_region", "map", "RoadRailway500m"),
        setup.MVTAPI("settlement-0m", "map", "Settlement0m"),
        setup.MVTAPI("water", "map", "Water"),
    ],
    "potential": [
        setup.MVTAPI("potentialarea_pv_agriculture_lfa-off_region", "map", "PotentialareaPVAgricultureLFAOff"),
        setup.MVTAPI("potentialarea_pv_road_railway_region", "map", "PotentialareaPVRoadRailway"),
        setup.MVTAPI("potentialarea_wind_stp_2018_vreg", "map", "PotentialareaWindSTP2018Vreg"),
        setup.MVTAPI("potentialarea_wind_stp_2027_repowering", "map", "PotentialareaWindSTP2027Repowering"),
        setup.MVTAPI(
            "potentialarea_wind_stp_2027_search_area_forest_area",
            "map",
            "PotentialareaWindSTP2027SearchAreaForestArea",
        ),
        setup.MVTAPI(
            "potentialarea_wind_stp_2027_search_area_open_area",
            "map",
            "PotentialareaWindSTP2027SearchAreaOpenArea",
        ),
        setup.MVTAPI("potentialarea_wind_stp_2027_vr", "map", "PotentialareaWindSTP2027VR"),
    ],
    "results": [setup.MVTAPI("results", "map", "Municipality")],
}

MAP_ENGINE_API_CLUSTERS = [
    setup.ClusterAPI("wind", "map", "WindTurbine", properties=["id"]),
    setup.ClusterAPI("pvroof", "map", "PVroof", properties=["id"]),
    setup.ClusterAPI("pvground", "map", "PVground", properties=["id"]),
    setup.ClusterAPI("hydro", "map", "Hydro", properties=["id"]),
    setup.ClusterAPI("biomass", "map", "Biomass", properties=["id"]),
    setup.ClusterAPI("combustion", "map", "Combustion", properties=["id"]),
    setup.ClusterAPI("gsgk", "map", "GSGK", properties=["id"]),
    setup.ClusterAPI("storage", "map", "Storage", properties=["id"]),
]

MAP_ENGINE_STYLES_FOLDER = "digiplan/static/config/"
MAP_ENGINE_ZOOM_LEVELS = {
    "municipality": setup.Zoom(8, 12),
}

MAP_ENGINE_CHOROPLETHS = [
    setup.Choropleth("population_statusquo", layers=["municipality"], title=_("Einwohner_innenzahl"), unit=_("")),
    setup.Choropleth(
        "population_density_statusquo",
        layers=["municipality"],
        title=_("Einwohner_innenzahl pro km²"),
        unit=_(""),
    ),
    setup.Choropleth("employees_statusquo", layers=["municipality"], title=_("Beschäftigte"), unit=_("")),
    setup.Choropleth("companies_statusquo", layers=["municipality"], title=_("Betriebe"), unit=_("")),
    setup.Choropleth("capacity_statusquo", layers=["municipality"], title=_("Installierte Leistung"), unit=_("MW")),
    setup.Choropleth(
        "capacity_square_statusquo",
        layers=["municipality"],
        title=_("Installierte Leistung pro qm"),
        unit=_("MW"),
    ),
    setup.Choropleth("wind_turbines_statusquo", layers=["municipality"], title=_("Anzahl Windturbinen"), unit=_("")),
    setup.Choropleth(
        "wind_turbines_square",
        layers=["municipality"],
        title=_("Anzahl Windturbinen pro qm"),
        unit=_(""),
    ),
    setup.Choropleth(
        "energy_statusquo",
        layers=["municipality"],
        title=_("Energie Erneuerbare"),
        unit=_("GWh"),
    ),
    setup.Choropleth(
        "energy_2045",
        layers=["municipality"],
        title=_("Energie Erneuerbare"),
        unit=_("GWh"),
    ),
    setup.Choropleth(
        "energy_share_statusquo",
        layers=["municipality"],
        title=_("Anteil Erneuerbare Energien am Strombedarf"),
        unit=_("%"),
    ),
    setup.Choropleth(
        "energy_capita_statusquo",
        layers=["municipality"],
        title=_("Gewonnene Energie aus EE je EW"),
        unit=_("MWh"),
    ),
    setup.Choropleth(
        "energy_capita_2045",
        layers=["municipality"],
        title=_("Gewonnene Energie aus EE je EW"),
        unit=_("MWh"),
    ),
    setup.Choropleth(
        "energy_square_statusquo",
        layers=["municipality"],
        title=_("Gewonnene Energie aus EE je km²"),
        unit=_("MWh"),
    ),
    setup.Choropleth(
        "energy_square_2045",
        layers=["municipality"],
        title=_("Gewonnene Energie aus EE je km²"),
        unit=_("MWh"),
    ),
    setup.Choropleth(
        "electricity_demand_statusquo",
        layers=["municipality"],
        title=_("Strombedarf"),
        unit=_("MWh"),
    ),
    setup.Choropleth(
        "electricity_demand_capita_statusquo",
        layers=["municipality"],
        title=_("Strombedarf pro EinwohnerIn"),
        unit=_("MWh"),
    ),
    setup.Choropleth(
        "heat_demand_statusquo",
        layers=["municipality"],
        title=_("Wärmebedarf"),
        unit=_("MWh"),
    ),
    setup.Choropleth(
        "heat_demand_capita_statusquo",
        layers=["municipality"],
        title=_("Wärmebedarf pro EinwohnerIn"),
        unit=_("MWh"),
    ),
    setup.Choropleth(
        "batteries_statusquo",
        layers=["municipality"],
        title=_("Anzahl Batteriespeicher"),
        unit=_("#"),
    ),
    setup.Choropleth(
        "batteries_capacity_statusquo",
        layers=["municipality"],
        title=_("Kapazität Batteriespeicher"),
        unit=_("MWh"),
    ),
]

MAP_ENGINE_POPUPS = [
    setup.Popup(
        "municipality",
        popup_at_default_layer=False,
        choropleths=[
            "population_statusquo",
            "population_density_statusquo",
            "employees_statusquo",
            "companies_statusquo",
            "capacity_statusquo",
            "capacity_square_statusquo",
            "wind_turbines_statusquo",
            "wind_turbines_square_statusquo",
            "energy_statusquo",
            "energy_2045",
            "energy_share_statusquo",
            "energy_capita_statusquo",
            "energy_capita_2045",
            "energy_square_statusquo",
            "energy_square_2045",
            "electricity_demand_statusquo",
            "electricity_demand_capita_statusquo",
            "heat_demand_statusquo",
            "heat_demand_capita_statusquo",
            "batteries_statusquo",
            "batteries_capacity_statusquo",
        ],
    ),
    setup.Popup(
        "wind",
        popup_at_default_layer=True,
    ),
    setup.Popup(
        "pvground",
        popup_at_default_layer=True,
    ),
    setup.Popup(
        "pvroof",
        popup_at_default_layer=True,
    ),
    setup.Popup(
        "hydro",
        popup_at_default_layer=True,
    ),
    setup.Popup(
        "biomass",
        popup_at_default_layer=True,
    ),
    setup.Popup(
        "combustion",
        popup_at_default_layer=True,
    ),
    setup.Popup(
        "gsgk",
        popup_at_default_layer=True,
    ),
    setup.Popup(
        "storage",
        popup_at_default_layer=True,
    ),
]
