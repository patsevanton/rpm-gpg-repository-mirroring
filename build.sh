#!/bin/bash

list_dependencies=(rpm-build rpmdevtools)

for i in ${list_dependencies[*]}
do
    if ! rpm -qa | grep -qw $i; then
        echo "__________Dont installed '$i'__________"
        #yum -y install $i
    fi
done

spectool -g -R SPECS/rpm-gpg-repository-mirroring.spec
rpmbuild -bb --define "_topdir $PWD" SPECS/rpm-gpg-repository-mirroring.spec
