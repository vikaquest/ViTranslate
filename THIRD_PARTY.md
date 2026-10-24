# Сторонние компоненты

MIT-лицензия `LICENSE-worker` относится к опубликованному коду модуля, установщика
и примеров. Она не распространяется на закрытый интерфейс ViTranslate,
модели перевода и сторонние библиотеки.

| Компонент | Роль | Лицензия / источник |
|---|---|---|
| Argos Translate | Источник готовых пакетов моделей RU ↔ EN | [Проект](https://github.com/argosopentech/argos-translate), [MIT для кода Argos](https://github.com/argosopentech/argos-translate/blob/master/LICENSE) |
| CTranslate2 4.8.2 | Выполнение модели на CPU | [MIT](https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE) |
| SentencePiece 0.2.2 | Разбиение текста на токены и сборка результата | [Apache-2.0](https://github.com/google/sentencepiece/blob/master/LICENSE) |

Полный Python-пакет `argostranslate` в этом примере не требуется: воркер
читает пакеты моделей непосредственно через CTranslate2 и SentencePiece.
Дополнительные зависимости этих библиотек устанавливает pip; их версии
и уведомления можно посмотреть через `python -m pip list` и `python -m pip show`.

Модели — отдельные сторонние файлы. Их веса не публикуются в этом репозитории:
установщик получает пакеты с официального сервера, указанного в
[индексе Argos](https://github.com/argosopentech/argospm-index).
В пакете сохраняется исходный `README.md` с указанием авторов, источников
данных и относящихся к ним условий. MIT-лицензию кода Argos нельзя считать
единой лицензией всех весов и обучающих наборов. Для перераспространения
пакетов учитывайте их собственные сведения об авторстве и условиях.

Пакеты `translate-ru_en-1_9` и `translate-en_ru-1_9` указывают автором
Aleksey Kutashov; их metadata содержит
[ссылку на описание моделей](https://community.libretranslate.com/t/new-argos-model-en-ru-and-ru-en/872/).
SHA-256 файлов, использованных для этого примера, приведены в `models.lock.json`.
