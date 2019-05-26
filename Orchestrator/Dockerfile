FROM alpine:3.7
ENV TEAM_ID=CC_260_284_291_297
EXPOSE 3000
ADD package.json /tmp/package.json
RUN apk add --update nodejs
RUN cd /tmp && npm install
RUN mkdir -p /opt/app && cp -a /tmp/node_modules /opt/app/
ADD . /opt/app
WORKDIR /opt/app/APP_API_ACTS
CMD ["node","app.acts.js"]
