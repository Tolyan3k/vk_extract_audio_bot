# vk-extract-audio-from-video-bot

## Для чего нужен

Бот для соц. сети ВКонтакте, позволяющий извлекать из видео звуковую дорожку и затем прослушивать полученное аудио в виде *аудиозаписи*

Бот может быть полезен тем, кто хочет прослушать видеоподкасты или интервью в аудио формате, не выходя за пределы соц. сети.

На данный момент поддерживает видео до 10 минут, переданные через сообщение в виде *вложения*

## Архитектура

![Здесь будет картинка с архитектурой][architecture image]: https://i.ibb.co/RzfVbb8/image.png

## Тесты

- [Тесты на уровне пользователя][user-level tests]

## Пример взамодействия с ботом

![Пример взамодействия с ботом][bot work example image]

## Требования

- Python 3.10
- MongoDB
- FFmpeg
- Heroku CLI (Для деплоя)

## Установка

1. Python
    > pip install -r requirements
2. FFmpeg

    - При деплое на Heroku

    В настройках добавить *Buildpack*:
    > [https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git][heroku buildpack link]

    - При запуске со своего ПК

        1. Скачать **[FFmpeg][ffmpeg]**

        2. Из скачанного архива перекинуть файлы из *bin/* в папку со скриптами Python

<!-- -->

[ffmpeg]: https://ffmpeg.org/

[user-level tests]: https://docs.google.com/document/d/1wF3ij4__Fz41tzWrg7cdNFjW61Sc9YVp2clQEnLOYcI/edit?usp=sharing

[heroku buildpack link]: https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

<!-- Image links -->

[bot work example image]: https://i.ibb.co/QkNHZCk/2022-02-17-142927.png

[architecture image]: ""
