FROM python:3.12
# create directory /app under root, use it as working directory from now on
WORKDIR app
# copy local files into image filesystem, format: FROM <local dir> <image dir>
COPY temp_store temp_store
COPY pages pages
COPY pyproject.toml .
COPY README.md .
# execute bash commands (one time during build) to add third party dependencies in the image
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install poetry
RUN poetry install
# command to execute on container startup
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "temp_store.web:app"]
