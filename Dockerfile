FROM python:3-alpine
MAINTAINER renothing 'frankdot@qq.com'
LABEL app='qq' version='0.1.1' tags='qqbot' description='qqbot plugin for drone'
#set language enviroments
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
#install software
#RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && apk update && \ 
RUN apk update && \
 apk add --no-cache \
 tiff-dev \
 zlib-dev \
 jpeg-dev \
 freetype-dev \
 lcms2-dev \
 libwebp-dev \
 tcl-dev \
 tk-dev && \
#add build deps
 apk add --virtual .build-deps  \
 bzip2-dev \
 gcc \
 libc-dev \
 linux-headers \
 make \
 openssl \
 openssl-dev \
 readline-dev \
 xz-dev && \
 mkdir -p /root/.pip && \
 pip install six requests Pillow bottle && \
 apk del .build-deps && \
 rm -rf /var/cache/apk/*
#install app
WORKDIR /app/src
COPY src $WORKDIR
#VOLUME [/app/src/cookie]
#forwarding port
EXPOSE 8888
#set default command
ENTRYPOINT ["python","run.py"]
CMD ["--no-gui","--http"]
