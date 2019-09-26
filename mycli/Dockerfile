FROM isabl/cli

# install mycli
COPY . /code
RUN pip install /code && rm -rf /code

# add entry point
ENTRYPOINT ["mycli"]
