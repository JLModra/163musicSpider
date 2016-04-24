#!/bin/sh
#!/mongodb-linux-x86_64-ubuntu1404-3.2.5/bin

python musicSpider.py
./mongodb-linux-x86_64-ubuntu1404-3.2.5/bin/mongoexport -d netease_music_list -c music_list_info -o /163musicSpider/music_list_info.csv
python mail.py
