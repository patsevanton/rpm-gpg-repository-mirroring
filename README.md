# rpm-gpg-repository-mirroring - Скрипт для скачивания RPM пакетов из репозиториев, для которых нельзя сделать RPM зеркало

В некоторых организациях с серверов нет доступа в интернет. В таких случаях делают зеркала основных репозиториев.
Цель данного поста рассказать о скрипте, который скачивает последние версии rpm пакетов из репозиториев Grafana, Kubernetes, Gitlab, packagecloud.io и так далее.

Какие преимущества использования скрипта перед reposync
 - rpm-gpg-repository-mirroring может скачивать все rpm пакеты, начиная с определенной версии
 - rpm-gpg-repository-mirroring может скачивать последние N версий rpm пакетов
 - rpm-gpg-repository-mirroring значительно экономит трафик в сравнении с reposync
 - rpm-gpg-repository-mirroring значительно экономит дисковое пространство в сравнении с reposync

![](https://habrastorage.org/webt/_m/ji/ql/_mjiqlrkde3cku5lfqwr7muzyq4.png)

## Выключаем Selinux
```
sudo sed -i s/^SELINUX=.*$/SELINUX=disabled/ /etc/selinux/config
sudo reboot
```

## Установка и запуск rpm-gpg-repository-mirroring (epel-release нужен для nginx)
```
yum install -y epel-release
yum -y install yum-plugin-copr
yum copr enable antonpatsev/rpm-gpg-repository-mirroring
yum -y install rpm-gpg-repository-mirroring
```

## Настройка rpm-gpg-repository-mirroring
Редактируем файл `/etc/rpm-gpg-repository-mirroring.conf`
В нем все подробно описано.

### Репозиторий, с которого нужно скачать все последние rpm пакеты начиная с определенной версии. Пример Grafana

Создадим /etc/yum.repos.d/grafana.repo со следующим содержимым:
```
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=0
enabled=1
gpgcheck=0
gpgkey=https://packages.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
```

Конфиг /etc/rpm-gpg-repository-mirroring.conf:
```
# Директория, в которых будут создаваться rpm репозитории
DOWNLOAD_DIR=/var/www/repos

# репозитории, rpm которых будут скачиваться начиная с определенной версии, указаной в значении
REPOS={"grafana":"6.5.3"}
```

Запускаем скрипт
```
rpm-gpg-repository-mirroring
```

После запуска скрипта в директории /var/www/repos должна появится директория grafana, содержащая rpm репозиторий.
```
ls -1 /var/www/repos/grafana/
grafana-6.5.3-1.x86_64.rpm
grafana-6.6.0-1.x86_64.rpm
grafana-6.6.1-1.x86_64.rpm
grafana-6.6.2-1.x86_64.rpm
grafana-6.7.0-1.x86_64.rpm
grafana-6.7.0-test.x86_64.rpm
grafana-6.7.1-1.x86_64.rpm
grafana-6.7.2-1.x86_64.rpm
grafana-6.7.3-1.x86_64.rpm
grafana-6.7.4-1.x86_64.rpm
grafana-7.0.0-1.x86_64.rpm
grafana-7.0.1-1.x86_64.rpm
grafana-7.0.2-1.x86_64.rpm
grafana-7.0.3-1.x86_64.rpm
repodata
```

### Репозиторий, с которого нужно скачать все последние rpm пакеты начиная с определенной версии + N последних версий определенных rpm пакетов. Пример Kubernetes

Создадим /etc/yum.repos.d/kubernetes.repo со следующим содержимым:

```
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
# c опцией repo_gpgcheck=1 скрипт выдает ошибку: repomd.xml signature could not be verified for kubernetes
```

Конфиг /etc/rpm-gpg-repository-mirroring.conf:
```
# Директория, в которых будут создаваться rpm репозитории
DOWNLOAD_DIR=/var/www/repos

# репозитории, rpm которых будут скачиваться начиная с определенной версии, указаной в значении
REPOS={"kubernetes":"1.17.6"}

# Для всех репозиторией, в которых есть rpm-пакет, совпадающий с ключом, необходимо скачать последние N версии этих rpm пакетов.
# Где N указываетя в значении.
CUT_AFTER={"rkt":2,"kubernetes-cni":2,"cri-tools":2}
```

После запуска скрипта в директории /var/www/repos должна появится директория kubernetes, содержащая rpm репозиторий.
```
ls -1 /var/www/repos/kubernetes/
cri-tools-1.12.0-0.x86_64.rpm
cri-tools-1.13.0-0.x86_64.rpm
kubeadm-1.17.6-0.x86_64.rpm
kubeadm-1.17.7-0.x86_64.rpm
kubeadm-1.18.0-0.x86_64.rpm
kubeadm-1.18.1-0.x86_64.rpm
kubeadm-1.18.2-0.x86_64.rpm
kubeadm-1.18.3-0.x86_64.rpm
kubeadm-1.18.4-0.x86_64.rpm
kubectl-1.17.6-0.x86_64.rpm
kubectl-1.17.7-0.x86_64.rpm
kubectl-1.18.0-0.x86_64.rpm
kubectl-1.18.1-0.x86_64.rpm
kubectl-1.18.2-0.x86_64.rpm
kubectl-1.18.3-0.x86_64.rpm
kubectl-1.18.4-0.x86_64.rpm
kubelet-1.17.6-0.x86_64.rpm
kubelet-1.17.7-0.x86_64.rpm
kubelet-1.18.0-0.x86_64.rpm
kubelet-1.18.1-0.x86_64.rpm
kubelet-1.18.2-0.x86_64.rpm
kubelet-1.18.3-0.x86_64.rpm
kubelet-1.18.4-0.x86_64.rpm
kubernetes-cni-0.6.0-0.x86_64.rpm
kubernetes-cni-0.7.5-0.x86_64.rpm
repodata
rkt-1.26.0-1.x86_64.rpm
rkt-1.27.0-1.x86_64.rpm
```

### Репозиторий, с которого нужно скачать N последних версий определенных rpm пакетов. Пример Prometheus

Создадим /etc/yum.repos.d/prometheus.repo со следующим содержимым:
```
[prometheus-7]
name=prometheus
baseurl=https://packagecloud.io/prometheus-rpm/release/el/$releasever/$basearch
repo_gpgcheck=0
enabled=1
gpgkey=https://packagecloud.io/prometheus-rpm/release/gpgkey
       https://raw.githubusercontent.com/lest/prometheus-rpm/master/RPM-GPG-KEY-prometheus-rpm
gpgcheck=1
metadata_expire=300
```

Конфиг /etc/rpm-gpg-repository-mirroring.conf:
```
# Директория, в которых будут создаваться rpm репозитории
DOWNLOAD_DIR=/var/www/repos

# ключ - репозиторий. значение: количество последних версий, которые необходимо скачать-для-всех-rpm-пакетов-в-репозитории.
# Пример: Для репозитория prometheus-7 нужно скачать последние 4 версии rpm пакетов.
#NUMBER_PACKAGE_IN_REPO={"prometheus-7":4}
```


После запуска скрипта в директории /var/www/repos должна появится директория prometheus-7, содержащая rpm репозиторий.
```
ls -1 /var/www/repos/prometheus-7/
alertmanager-0.19.0-2.el7.centos.x86_64.rpm
alertmanager-0.20.0-2.el7.centos.x86_64.rpm
alertmanager-0.20.0-2.el7.x86_64.rpm
alertmanager-0.21.0-2.el7.x86_64.rpm
apache_exporter-0.7.0-1.el7.centos.x86_64.rpm
apache_exporter-0.8.0-1.el7.x86_64.rpm
bind_exporter-0.3.0-1.el7.centos.x86_64.rpm
bind_exporter-0.3.0-1.el7.x86_64.rpm
blackbox_exporter-0.16.0-1.el7.centos.x86_64.rpm
blackbox_exporter-0.16.0-1.el7.x86_64.rpm
collectd_exporter-0.4.0-1.el7.centos.x86_64.rpm
collectd_exporter-0.4.0-1.el7.x86_64.rpm
consul_exporter-0.4.0-1.el7.centos.x86_64.rpm
consul_exporter-0.6.0-1.el7.centos.x86_64.rpm
consul_exporter-0.6.0-1.el7.x86_64.rpm
consul_exporter-0.7.0-1.el7.x86_64.rpm
elasticsearch_exporter-1.0.1-1.el7.centos.x86_64.rpm
elasticsearch_exporter-1.0.2-1.el7.centos.x86_64.rpm
elasticsearch_exporter-1.1.0-1.el7.centos.x86_64.rpm
elasticsearch_exporter-1.1.0-1.el7.x86_64.rpm
exporter_exporter-0.3.0-2.el7.centos.x86_64.rpm
exporter_exporter-0.3.0-2.el7.x86_64.rpm
exporter_exporter-0.4.0-0.el7.x86_64.rpm
exporter_exporter-0.4.0-1.el7.x86_64.rpm
graphite_exporter-0.4.2-1.el7.centos.x86_64.rpm
graphite_exporter-0.6.2-1.el7.centos.x86_64.rpm
graphite_exporter-0.6.2-1.el7.x86_64.rpm
graphite_exporter-0.7.0-1.el7.x86_64.rpm
haproxy_exporter-0.10.0-1.el7.centos.x86_64.rpm
haproxy_exporter-0.10.0-1.el7.x86_64.rpm
iperf3_exporter-0.1.2-1.el7.x86_64.rpm
iperf3_exporter-0.1.3-1.el7.x86_64.rpm
jmx_exporter-0.12.0-1.el7.centos.noarch.rpm
jolokia_exporter-1.3.1-1.el7.x86_64.rpm
junos_exporter-0.9.6-1.el7.x86_64.rpm
junos_exporter-0.9.6-2.el7.x86_64.rpm
keepalived_exporter-0.4.0-1.el7.x86_64.rpm
keepalived_exporter-0.4.0-2.el7.x86_64.rpm
memcached_exporter-0.6.0-1.el7.centos.x86_64.rpm
memcached_exporter-0.6.0-1.el7.x86_64.rpm
mysqld_exporter-0.10.0-1.el7.centos.x86_64.rpm
mysqld_exporter-0.11.0-1.el7.centos.x86_64.rpm
mysqld_exporter-0.12.1-1.el7.centos.x86_64.rpm
mysqld_exporter-0.12.1-1.el7.x86_64.rpm
nginx_exporter-0.4.1-1.el7.centos.x86_64.rpm
nginx_exporter-0.4.1-1.el7.x86_64.rpm
nginx_exporter-0.7.0-1.el7.x86_64.rpm
nginx_exporter-0.8.0-1.el7.x86_64.rpm
node_exporter-1.0.0-1.el7.x86_64.rpm
node_exporter-1.0.1-1.el7.x86_64.rpm
ping_exporter-0.4.6-1.el7.centos.x86_64.rpm
ping_exporter-0.4.6-1.el7.x86_64.rpm
process_exporter-0.5.0-1.el7.centos.x86_64.rpm
process_exporter-0.5.0-1.el7.x86_64.rpm
process_exporter-0.6.0-1.el7.x86_64.rpm
process_exporter-0.6.0-2.el7.x86_64.rpm
prometheus-1.8.0-1.el7.centos.x86_64.rpm
prometheus-1.8.1-1.el7.centos.x86_64.rpm
prometheus-1.8.2-1.el7.centos.x86_64.rpm
prometheus-1.8.2-1.el7.x86_64.rpm
prometheus2-2.18.1-1.el7.x86_64.rpm
prometheus2-2.18.2-1.el7.x86_64.rpm
prometheus2-2.19.0-1.el7.x86_64.rpm
prometheus2-2.19.1-1.el7.x86_64.rpm
pushgateway-1.2.0-1.el7.x86_64.rpm
rabbitmq_exporter-0.26.0-1.el7.centos.x86_64.rpm
rabbitmq_exporter-0.28.0-1.el7.centos.x86_64.rpm
rabbitmq_exporter-0.28.0-1.el7.x86_64.rpm
redis_exporter-1.3.5-1.el7.centos.x86_64.rpm
redis_exporter-1.3.5-1.el7.x86_64.rpm
redis_exporter-1.6.0-1.el7.x86_64.rpm
redis_exporter-1.8.0-1.el7.x86_64.rpm
repodata
sachet-0.0.8-1.el7.centos.x86_64.rpm
sachet-0.2.0-1.el7.centos.x86_64.rpm
sachet-0.2.0-1.el7.x86_64.rpm
sachet-0.2.3-1.el7.x86_64.rpm
sachet-debuginfo-0.2.0-1.el7.centos.x86_64.rpm
sachet-debuginfo-0.2.0-1.el7.x86_64.rpm
smokeping_prober-0.3.0-1.el7.centos.x86_64.rpm
smokeping_prober-0.3.0-1.el7.x86_64.rpm
ssl_exporter-0.6.0-1.el7.centos.x86_64.rpm
ssl_exporter-0.6.0-1.el7.x86_64.rpm
ssl_exporter-1.0.0-1.el7.x86_64.rpm
ssl_exporter-1.0.1-1.el7.x86_64.rpm
statsd_exporter-0.13.0-1.el7.centos.x86_64.rpm
statsd_exporter-0.14.1-1.el7.centos.x86_64.rpm
statsd_exporter-0.14.1-1.el7.x86_64.rpm
statsd_exporter-0.15.0-1.el7.x86_64.rpm
thanos-0.11.0-1.el7.x86_64.rpm
thanos-0.12.0-1.el7.x86_64.rpm
thanos-0.12.1-1.el7.x86_64.rpm
thanos-0.12.2-1.el7.x86_64.rpm
```
