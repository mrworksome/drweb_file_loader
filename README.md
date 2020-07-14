# drweb_file_loader
Хранилище файлов с доступом по http

Реализовать демон, который предоставит HTTP API для загрузки (upload) ,
скачивания (download) и удаления файлов.

# Upload
- получив файл от клиента, демон возвращает в отдельном поле http
response хэш загруженного файла
- демон сохраняет файл на диск в следующую структуру каталогов:
    store/ab/abcdef12345...
где "abcdef12345..." - имя файла, совпадающее с его хэшем.
/ab/  - подкаталог, состоящий из первых двух символов хэша файла.
Алгоритм хэширования - на ваш выбор.

* Загрузка происходит чанками(chunk) если выбранный файл является большим

# Download
Запрос на скачивание: клиент передаёт параметр - хэш файла. Демон ищет
файл в локальном хранилище и отдаёт его, если находит.

# Delete
Запрос на удаление: клиент передаёт параметр - хэш файла. Демон ищет
файл в локальном хранилище и удаляет его, если находит.

# Usage
- main.py - основная программа
- file_manager.py - обработчик фаилов
- model.py - Описание фаила до загрузки

Краткое описание работы программы

Добавил работу с MongoDB и для асинхронной работы с mongo установил Motor
После получения и записи фаила в дирректорию (dr_web_strore),
записываем описание фаила в базу.

После запуска основного скрипта(main.py) вся работа производтся по следующему
адресу (http://127.0.0.1/docs)
