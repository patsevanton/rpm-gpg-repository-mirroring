#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Программа для скачивания пакетов из yum-репозитория с определенными в конфиге условиями.
#
# Имена репозиториев, имена пакетов для каждого из репозиториев и набор версий для каждого из этих
# пакетов образуют нагруженное множесто repo_name_ver.
# Внутреннеее нагруженное множество в виде отношения имен пакетов к набору версий для каждого пакета,
# является нагрузкой к множеству репозиториев.

import glob
import json
import os
import shutil
import sys
import yum
import subprocess
from distutils.version import LooseVersion

# Имя конфига.
config = "/etc/rpm-gpg-repository-mirroring.conf"

# Получить словарь репозиторий->версия из конфига для условия, которое отсекает работу с версиями
# ниже чем в данной настройке.
def get_dict_repo(config):
	with open(config, "r") as f:
		for line in f:
			if "REPOS" in line:
				fields = line.strip().split("=")
				dict_repo=json.loads(fields[1])
				return dict_repo

# Получить дополнительное ограничение к условию выше:
# работать только с пакетами по истории не старше чем с глубиной,
# определяемой в словаре имемя_пакета->глубина_версии.
def get_dict_cut(config):
	with open(config, "r") as f:
		for line in f:
			if "CUT_AFTER" in line:
				fields = line.strip().split("=")
				name_count=json.loads(fields[1])
				return name_count

# Получить ограничение по количеству свежих версий в рамках всех пакетов репозитория.
# Действует для отдельного специального набора репозиторев,
# в которых не применяются два правила выше.
# репозиторий->глубина
def get_name_uni_count(config):
	with open(config, "r") as f:
		for line in f:
			if "NUMBER_PACKAGE_IN_REPO" in line:
				fields = line.strip().split("=")
				name_uni_count=json.loads(fields[1])
				return name_uni_count

# Объемлющий каталог для хранения скачиваемого.
def get_download_dir(config):
	with open(config) as f:
		for line in f:
			if "DOWNLOAD_DIR" in line:
				fields = line.strip().split("=")
				dir=fields[1]
				return dir

# Отдельная функция для записи файлов.
# Получает pkg и repo, которые нужно сохранять.
# TODO: repo вероятно излишен и может быть получен другим путём.
def save_po(pkg, repo):
	# Подготовка пути для сохранения.
	remote = pkg.returnSimple('relativepath')
	local = os.path.basename(remote)
	# Скачка в темповую директорию	- без этого хака лезла ошибка..
	local_wp = os.path.join(tmp, local)
	# Настройка yum-api для скачки.
	pkg.localpath = local_wp
	# Проверка существования файла, чтобы не качать снова.
	if os.path.isfile(download_dir + '/' + repo + '/' + str(pkg) + '.rpm'):
		return
	# Получение-скачивание необходимого пакета через yum-api.
	path = pkg.repo.getPackage(pkg, copy_local=1, cache = False)
	# Перемещение его из темповой директории.
	shutil.move(os.path.join(tmp, local), os.path.join(download_dir + '/' + repo, str(pkg) + '.rpm'))

# Причваение настроек в конфиге и инициализация глобального словаря.
name_count = get_dict_cut(config)
repo_name_ver = {}
repo_ver = get_dict_repo(config)
download_dir = get_download_dir(config)

# В этом цикле, часть логики совпадает со следующем.
# Отсутствующие здесь неспецифичные комментарии расположены в следующем цикле,
# где сторонней логики меньше, и понимать эту часть проще.
#
# Обработка логики первых двух настроек: прохождение по репозиторию объединяющему их.
if repo_ver is not None:
	for repo in repo_ver:
		yb = yum.YumBase()
		if not yb.setCacheDir():
			print >>sys.stderr, "Can't create a tmp. cachedir. "
			sys.exit(1)
		yb.repos.disableRepo('*')
		yb.repos.enableRepo(repo)

		if not os.path.exists(download_dir + '/' + repo):
			os.makedirs(download_dir + '/' + repo)
		tmp = download_dir + '/' + repo + '/tmp'
		if not os.path.exists(tmp):
			os.makedirs(tmp)
		else:
			files = glob.glob(tmp + '/*')
			for f in files:
				os.remove(f)

		repo_name_ver[repo] = {}
		ignore = False
		prev_name = None
		for pkg in sorted(yb.pkgSack.returnPackages(), reverse=True):
			if ignore == True and prev_name == pkg.name:
				continue
			if prev_name != pkg.name:
				ignore = False

			pkg.repo.copy_local = True
			pkg.repo.cache = 0

			# Если попали в имя, нужное второй настроке.
			if name_count is not None and pkg.name in name_count:
				# Текущая глубина всё ещё существует.
				if name_count[pkg.name] > 0:
					# Добавится или инициализируется запись в глобальный словарь.
					if pkg.name not in repo_name_ver[repo]:
						repo_name_ver[repo][pkg.name] = []
					repo_name_ver[repo][pkg.name].append(pkg.version + '-' + pkg.release)
					# Надо уменьшить текущую историю для будущего отслеживания.
					name_count[pkg.name] -= 1
					# Скачать.
					save_po(pkg, repo)
				# Имя всё еще остлеживаемое, но предел текущий глубины.
				else:
					# Удалить запись из переменной-словаря.
					name_count.pop(pkg.name, None)
					# Игнорировать следующие глубины в случае если попадётся то же имя.
					ignore = True
			# Если не попали под вторую настройку, а она взаимоисключает первую.
			else:
				# Для избранных номеров версий игнорировать все версии что ниже определенной.
				if LooseVersion(pkg.version) >= LooseVersion(repo_ver[repo]):
					if pkg.name not in repo_name_ver[repo]:
						repo_name_ver[repo][pkg.name] = []
					repo_name_ver[repo][pkg.name].append(pkg.version + '-' + pkg.release)
					save_po(pkg, repo)
			prev_name = pkg.name
		process = subprocess.Popen("/usr/bin/createrepo --update {0}/{1}".format(download_dir, repo), shell=True, stdout=subprocess.PIPE)
		output, error = process.communicate()
		print(output)

# Работа с репозиториями, к которым применяется третье ограничение на отсечение по количеству свежих версий.
#
# Получение значения настроек.
name_uni_count = get_name_uni_count(config)
# Для каждого репозитория как индекса словаря.
if name_uni_count is not None:
	for repo in name_uni_count:
		# Количество последних фиксируемых версий, полученное как значение от индекса.
		# Не константа - изменяется, чтобы определить остановку в работе.
		uni_tmp = name_uni_count[repo]

		# Необходимая инициализация для репозитория.
		yb = yum.YumBase()
		if not yb.setCacheDir():
			print >>sys.stderr, "Can't create a tmp. cachedir. "
			sys.exit(1)
		# Уточнение конкретного ограничивающего имени.
		yb.repos.disableRepo('*')
		yb.repos.enableRepo(repo)

		# Создание каталога для сохранения, если не существует.
		if not os.path.exists(download_dir + '/' + repo):
			os.makedirs(download_dir + '/' + repo)
		# Вычисление пути для специального временного каталога для скачки.
		tmp = download_dir + '/' + repo + '/tmp'
		# Создание этого каталога, если необходимо. Или очистка всех файлов внутри.
		if not os.path.exists(tmp):
			os.makedirs(tmp)
		else:
			files = glob.glob(tmp + '/*')
			for f in files:
				os.remove(f)
		# Необходимая инициализация словаря.
		repo_name_ver[repo] = {}
		# Флаг для необходимого своевременного перехода к следующему имени при логическом забеге вперёд.
		ignore = False
		# Переменная для сохранения предыдущего имени пакета.
		prev_name = None
		# Итерация по отсортированным по свежести пакетам.
		for pkg in sorted(yb.pkgSack.returnPackages(), reverse=True):
			# Переместиться на следующую итерацию, если работается в рамках одного имени и надо игнорировать.
			if ignore == True and prev_name == pkg.name:
				continue
			# Здесь уже пришло новое имя пакета и с ним надо начинать работать, а не игнорировать изначально.
			if prev_name != pkg.name:
				ignore = False

			# Необходимые условия для yum-api чтобы гарантировать что пакет именно скачается.
			pkg.repo.copy_local = True
			pkg.repo.cache = 0

			# Пока ещё есть глубина для работы.
			if uni_tmp > 0:
				# Проверяется, присутствует ли уже имя в словаре и внутренний словарь инициализируется.
				if pkg.name not in repo_name_ver[repo]:
					repo_name_ver[repo][pkg.name] = []
				# Либо добавляется в набор необходимых версий для скачки.
				repo_name_ver[repo][pkg.name].append(pkg.version + '-' + pkg.release)
				# Текущее меньшение глубины.
				uni_tmp -= 1
				# Скачка файла.
				save_po(pkg, repo)
			# Достигнут лимит на отслеживаемые версии.
			# Возможно их меньше присутствует в репозитории чем надо отследить.
			# Интересоваться больше не имеет смысла.
			# Надо игнорировать итерации вперёд в рамках одного имени, то есть переходить к следующему имени.
			else:
				# Приведение переменной к первоначальному значению из конфига для последующих итераций.
				uni_tmp = name_uni_count[repo]
				ignore = True
			# Запоминание имени пакета для следующей итерации для сравнения на идентичность чтобы игнорировать.
			prev_name = pkg.name
		process = subprocess.Popen("/usr/bin/createrepo --update {0}/{1}".format(download_dir, repo), shell=True, stdout=subprocess.PIPE)
		output, error = process.communicate()
		print(output)


# Более красивая распечатка словаря.
def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

pretty(repo_name_ver)
#print repo_name_ver
