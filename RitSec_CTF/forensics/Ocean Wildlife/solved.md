Флаг: RS{f0ll0w_th3_5ea_Turtles}

Дают ZIP с двумя файлами: metadata.yaml и mystery_message_0.db3. YAML сразу подсказывает — это ROS2 rosbag, формат записи данных роботов. Внутри SQLite база с топиками, среди которых /draw_commands с 284 сообщениями типа std_msgs/String.
Достали сообщения из базы, распарсили CDR-сериализацию и получили JSON-команды двух типов: teleport (координаты x/y) и pen (цвет, толщина, вкл/выкл). Это путь черепашки из turtlesim — стандартного симулятора ROS.
pythonimport sqlite3, struct, json
cur.execute('SELECT data FROM messages WHERE topic_id=6 ORDER BY timestamp')
# парсим CDR: 4 байта заголовок + 4 байта длина + строка
Воспроизвели весь путь черепашки на холсте (координатная система turtlesim: начало снизу-слева, ось Y вверх) и получили изображение с флагом.
pythonfrom PIL import Image, ImageDraw
# teleport + pen_on → рисуем линию между точками