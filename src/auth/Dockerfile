ARG BASE_IMAGE=gitlab.macrodom.ru:5050/macrobank/base-images/python-v2

FROM $BASE_IMAGE

ARG SRC_NAMESPACE='--without dev'
ARG PYTHON_VER=3.11
ARG USERNAME=appuser

WORKDIR $APP_HOME

COPY src src
COPY src/auth/entrypoint.sh .
COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install $SRC_NAMESPACE && \
    chmod a+rwx -R . && \
    chmod a+rwx -R "/usr/local/lib/python${PYTHON_VER}"

# modify path variable
ENV PATH="$APP_HOME/.local/bin:$PATH"

USER $USERNAME

CMD sh entrypoint.sh
