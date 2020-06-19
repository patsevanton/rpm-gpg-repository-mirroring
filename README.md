# rpm-gpg-repository-mirroring - Скрипт для скачивания RPM пакетов из репозиториев, для которых нельзя сделать RPM зеркало

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

Диаграмма для репо kubernetes и grafana
![](https://habrastorage.org/webt/wd/8f/dj/wd8fdjxo6a-j1fevwuuiz8lkp4u.png)
