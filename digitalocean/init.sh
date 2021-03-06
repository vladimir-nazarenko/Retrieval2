adduser --home /home/vladimir vladimir
gpasswd -a vladimir sudo
su - vladimir
mkdir Downloads
cd Downloads
wget http://repo.yandex.ru/yandex-disk/yandex-disk_latest_amd64.deb
sudo dpkg -i yandex-disk_latest_amd64.deb
yandex-disk setup
yandex-disk sync > ydisklog.txt &
cd /home/vladimir
mkdir archives
mv Yandex.Disk/Загрузки/* archives/
cd archives
sudo apt-get update
sudo apt-get install build-essential p7zip-full git python3-lxml python3-pip libxml2-dev libxslt1-dev python3-libxml2 zlib1g-dev
sudo pip3 install cssselect
sudo pip3 install --upgrade lxml
sudo pip3 install pymorphy2
7za e BY.7z.001 > /dev/null &
cd ..
git clone https://github.com/vladimir-nazarenko/Retrieval2.git
fg
rm archives/BY.7z.*
cat archives/* > Retrieval2/big_by.xml
rm -r archives
cd Retrieval2
sed -i -- 's/&/&amp;/g' big_by.xml
python3 -u Main.py | tee main_logs.txt
python3 -u formatter.py | tee formatter_logs.txt
sudo add-apt-repository ppa:builds/sphinxsearch-rel22
sudo apt-get update
sudo apt-get install mysql-client mysql-server sphinxsearch
wget http://sphinxsearch.com/files/dicts/ru.pak
wget http://sphinxsearch.com/files/dicts/en.pak
mkdir ../dicts
mv *.pak ../dicts/
indexer --config sphinx.conf --all
sudo service sphinxsearch stop
sudo searchd --config sphinx.conf
mkdir queries
cd queries
wget http://romip.ru/tasks/2008/web2008_adhoc.xml.bz2
bzip2 web2008_adhoc.xml.bz2
wget http://romip.ru/relevance-tables/2008/web-adhoc/by/or_relevant-minus_table.xml.gz
gunzip or_relevant-minus_table.xml.gz
mv or_relevant-minus_table.xml 2008or_relevant-minus_table.xml
wget http://romip.ru/relevance-tables/2009/web-adhoc/by/or_relevant-minus_table.xml.gz
gunzip or_relevant-minus_table.xml.gz
mv or_relevant-minus_table.xml 2009or_relevant-minus_table.xml
sudo pip3 install pymysql