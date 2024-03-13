# First a base image has to be selected. I am using the official Python 3.12 image based on leightweight Alpine
FROM python:3.12-alpine

# RUN allows to execute arbitrary shell commands, creating a new file system layer
# Best Practice: create a dedicated user to run you application otherwise it is run a root
RUN busybox addgroup -S -g 6969 tempstore && busybox adduser -h /app -G tempstore -D -u 6969 tempstore

ARG POETRY_VERSION=1.7.1


ENV POETRY_VIRTUALENVS_IN_PROJECT=True

# The following installs Poetry in the given version
# one may use something called `here-documents` to write multiple lines of shell commands
# for this a few external dependencies have to be installed (GCC etc)
RUN <<EOF sh
    apk add --no-cache \
            curl \
            gcc \
            libressl-dev \
            musl-dev \
            libffi-dev
    python3 -m pip install --upgrade pip
    python3 -m pip install --no-cache-dir poetry==${POETRY_VERSION}
EOF

# change working directory to /app, would create it if not exists
WORKDIR /app

# copy local project files into image filesystem, format: COPY <local dir> <image dir>
# The .dockerignore file is used to control which files get copied
# Every COPY creates a new file file system layer
# I.e. the following command copies everything in the project dir that is not ignored to /app
COPY pages/* pages/
COPY temp_store/* temp_store/
COPY pyproject.toml .
COPY poetry.lock .

# change current user 
USER tempstore:tempstore

RUN poetry install


# command to execute on container startup
# first create the generic entry command (poetry in this case, which would allow us to run Python as well)
ENTRYPOINT ["poetry", "run"]
# CMD then runs poetry with the default flags
CMD ["uvicorn", "--host", "0.0.0.0", "temp_store.web:app"]
