%global _prefix /usr/local

Name:    rpm-gpg-repository-mirroring
Version: 0.6
Release: 2
Summary: Script for download RPM
Group:   Development Tools
License: ASL 2.0
Source0: rpm-gpg-repository-mirroring.py
Source1: nginx-rpm-gpg-repository-mirroring.conf
Source2: rpm-gpg-repository-mirroring.conf
Source3: rpm-gpg-repository-mirroring-cron
Requires: nginx
Requires: createrepo

%description
Script for download RPM

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}/%{_bindir}
%{__install} -m 755 %{SOURCE0} %{buildroot}/%{_bindir}/%{name}
mkdir -p %{buildroot}/etc/nginx/conf.d/
cp -a %{SOURCE1} %{buildroot}/etc/nginx/conf.d/
cp -a %{SOURCE2} %{buildroot}/etc/
mkdir -p %{buildroot}/etc/cron.d/
cp -a %{SOURCE3} %{buildroot}/etc/cron.d/
mkdir -p %{buildroot}/var/www/repos

%files
%{_bindir}/%{name}
/etc/nginx/conf.d/nginx-rpm-gpg-repository-mirroring.conf
/etc/rpm-gpg-repository-mirroring.conf
/etc/cron.d/rpm-gpg-repository-mirroring-cron
%dir /var/www/repos
