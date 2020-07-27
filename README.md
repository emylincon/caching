### Predictive Caching using Association
* under construction...

#### Note for alpine use
refere to [link](https://gist.github.com/orenitamar/f29fb15db3b0d13178c1c4dd611adce2) on how to install dependencies


### Installing FTP in Linux
```bash
sudo apt-get install vsftpd
```
#### Edit conf
* change to ```anonymous_enable=YES```
```bash
nano /etc/vsftpd.conf
```
###### /etc/vsftpd.conf
```markdown
# Allow anonymous FTP? (Disabled by default).
anonymous_enable=YES
```
* restart FTP Server
```bash
/etc/init.d/vsftpd restart
```
[Tutorial link](https://www.youtube.com/watch?v=GijFysBqaFs)

###### you can use the config file in this dir (vsftpd)
```bash
cp vsftpd.conf /etc/
```

* save files in `/srv/ftp` to be shared by ftp