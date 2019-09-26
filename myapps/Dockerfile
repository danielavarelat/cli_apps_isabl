FROM isabl/cli

# install myapps
COPY . /code
RUN pip install /code && rm -rf /code

# add entry point
ENTRYPOINT ["myapps"]
