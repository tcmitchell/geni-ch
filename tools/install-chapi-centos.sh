#!/bin/bash

CHAPI_LOG_DIR=/var/log/geni-chapi

echoerr() { echo "$@" 1>&2; }

# Exit on error
set -e
# Echo commands with variables expanded
set -x

# Create the chapi log directory
if [ ! -d "${CHAPI_LOG_DIR}" ]; then
  sudo mkdir -p "${CHAPI_LOG_DIR}"
  sudo chown apache.apache "${CHAPI_LOG_DIR}"
fi

TMP_DIR=/tmp/chapi-install
if [ -x "${TMP_DIR}" ]; then
  echoerr "Temporary build directory ${TMP_DIR} exists."
  echoerr "Please remove it and run this script again."
  exit 1
fi

# Find out where this script lives. It should be in the
# "tools" directory of a chapi tree.
TOOLS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CHAPI_DIR="${TOOLS_DIR}"/..

SHARE_DIR=/usr/share/geni-ch

# Make a directory for gcf to live in
if [ ! -d "${SHARE_DIR}" ]; then
  sudo /bin/mkdir -p "${SHARE_DIR}"
fi

mkdir "${TMP_DIR}"
cd "${TMP_DIR}"
mkdir -p chapi/chapi
cp -r "${CHAPI_DIR}" chapi/chapi
# Clean up any git cruft that got copied
find chapi -name '.git*' -delete
cd chapi

# At this point, I'm in /tmp/chapi-install/chapi

git clone https://github.com/GENI-NSF/geni-soil.git
ln -s geni-soil AMsoil
cd AMsoil

# fix up the amsoil directory
for pl in chrm chapiv1rpc sarm marm csrm logging opsmon flaskrest pgch
do
    sudo ln -s ../../../chapi/plugins/$pl src/plugins/$pl
done
# Remove unused AMsoil plugins
for pl in dhcprm dhcpgeni3 mailer worker geniv3rpc
do
    sudo rm -f src/plugins/$pl
done

# tar up chapi and then the whole package
cd ../..
tar cfpz chapi.tgz chapi
cp chapi/chapi/tools/install_ch .
tar cfp chapi_installer.tar chapi.tgz install_ch
#./install_ch
sudo tar pxfz chapi.tgz -o -C /usr/share/geni-ch
GCFDIR=$(readlink /usr/share/geni-ch/gcf)
if [ ! -h /usr/share/geni-ch/gcf ]; then
  ln -s $GCFDIR /usr/share/geni-ch/gcf
fi

# allow www-data to write to some AMsoil directories
sudo chown apache.apache /usr/share/geni-ch/chapi/AMsoil/deploy
sudo chown apache.apache /usr/share/geni-ch/chapi/AMsoil/log

# sudo chmod +w /etc/geni-ch/settings.php

# return home, we're in TMP_DIR and it's about to be deleted
cd
# Clean up the temp directory
sudo rm -rf "${TMP_DIR}"

#have to build chapi
cd "${HOME}"/chapi
autoreconf --install
./configure --prefix=/usr --sysconfdir=/etc --bindir=/usr/local/bin --sbindir=/usr/local/sbin
make
sudo make install



