FROM python:3-alpine

WORKDIR /usr/app

ADD requirements.txt .

RUN set -ex \
    && apk add --no-cache --virtual .build-deps zlib-dev jpeg-dev build-base \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r requirements.txt \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps

EXPOSE 8000
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD . .

CMD ["gunicorn", "-w 10", "-b :8000", "app:app"]