#!/bin/sh
#!/mongodb-linux-x86_64-ubuntu1404-3.2.5/bin

python musicSpider.py
./mongoexport -d netease_music_list -c music_list_info -o ../../music_list_info.csv
./mongoexport -d netease_music_list -c debug_info -o ../../debug_info
python mail.py
