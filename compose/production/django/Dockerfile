
# Manuals from
# https://pythonspeed.com/articles/conda-docker-image-size/
# https://pythonspeed.com/articles/activate-conda-dockerfile/
# https://jcristharif.com/conda-docker-tips.html
FROM continuumio/miniconda3 AS build

ENV PYTHONDONTWRITEBYTECODE=true

# Install the package as normal:
COPY environment.yml .
RUN conda env create -f environment.yml

# Install conda-pack:
RUN conda install --freeze-installed -c conda-forge conda-pack

# Use conda-pack to create a standalone environment
# in /venv:
RUN conda-pack -n enershelf -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# Clean conda and remove unnecessary files
RUN \
  conda clean -afy \
  && find /opt/conda/ -follow -type f -name '*.a' -delete \
  && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
  && find /opt/conda/ -follow -type f -name '*.js.map' -delete

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack


# The runtime-stage image; we can use Debian as the
# base image since the Conda env also includes Python
# for us.
FROM debian:buster-slim AS runtime

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  && apt-get install -y git \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # Only for django-distill (remove later)
  && apt-get install -y ca-certificates \
  && update-ca-certificates \
  # Locales de-De
  && apt-get install -y locales \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django \
    && adduser --system --ingroup django django

RUN sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE:en
ENV LC_ALL de_DE.UTF-8

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

# install requirements
WORKDIR /tmp
SHELL ["/bin/bash", "-c"]
COPY ./pyproject.toml ./poetry.lock ./
RUN source /venv/bin/activate && python -m pip install --upgrade pip && pip install --no-cache-dir poetry && poetry install --no-root --without dev
RUN source /venv/bin/activate && pip install --trusted-host github.com git+https://github.com/henhuy/django-raster.git@djagora

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start

ENV BASH_ENV "/home/django/.bashrc"
RUN echo "source /venv/bin/activate" > /home/django/.bashrc

COPY . /app

RUN chown -R django /app

USER django

WORKDIR /app
RUN mkdir staticfiles

ENTRYPOINT ["/entrypoint"]
