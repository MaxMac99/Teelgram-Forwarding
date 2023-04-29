# Telegram Forwarding

A tool to forward telegram messages from one chat to another. This may be a group or a person.

## Setup

Before starting get an API ID and API hash.

Go to [https://my.telegram.org/](https://my.telegram.org/), login with the phone number and go to ['API development tools'](https://my.telegram.org/apps).
The app has to be registered in order to get the API ID and API hash.
Create a telegram-api.env file similar to telegram-api.example.env and enter the API ID, API hash, phone number and password.

## Start

It is recommended to use docker to start the app.
First the app has to test the connection and configure the chats that should be forwarded.

In order to do so start it by running `docker-compose run telegramforwarding`.
A wizard is shown at first start to configure everything correctly.
It saves the configuration in `./config`.
After that the service can be startet in daemon mode via `docker-compose up -d`.
