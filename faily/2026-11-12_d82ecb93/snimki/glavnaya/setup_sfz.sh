#!/bin/sh
# Everything the two-library renders need, next to this script (music/):
#   VSCO-2-CE/        the VSCO samples (branch master)
#   vsco-sfz/         VSCO's SFZ files (branch SFZ, only the .sfz) with links to the sample folders
#   sso/              Sonatina Symphonic Orchestra (samples + SFZ)
#   sfizz/            the SFZ engine, built as a shared library (libsfizz.so)
# Needs git, cmake, a C++ compiler, libsndfile1-dev; ≈ 8 GB of disk with the .git folders (≈ 4.4 GB without).
set -e
cd "$(dirname "$0")"
[ -d VSCO-2-CE ] || git clone --depth 1 https://github.com/sgossner/VSCO-2-CE
[ -d sso ] || git clone --depth 1 https://github.com/peastman/sso
if [ ! -d vsco-sfz ]; then
  git clone -q --filter=blob:none --no-checkout --depth 1 --branch SFZ https://github.com/sgossner/VSCO-2-CE vsco-sfz-src
  (cd vsco-sfz-src && git sparse-checkout set --no-cone '*.sfz' && git checkout -q SFZ)
  mkdir vsco-sfz && cp vsco-sfz-src/*.sfz vsco-sfz/ && rm -rf vsco-sfz-src
  for d in Brass Keys Percussion Strings Woodwinds "VSCO 1 Percussion" "Miscellania Raw"; do
    ln -s "../VSCO-2-CE/$d" "vsco-sfz/$d"
  done
fi
if [ ! -f sfizz/bs/library/lib/libsfizz.so ]; then
  [ -d sfizz ] || git clone -q --depth 1 --recurse-submodules --shallow-submodules https://github.com/sfztools/sfizz
  mkdir -p sfizz/bs && cd sfizz/bs
  cmake .. -DCMAKE_BUILD_TYPE=Release -DSFIZZ_JACK=OFF -DSFIZZ_RENDER=OFF -DSFIZZ_SHARED=ON \
           -DSFIZZ_LV2=OFF -DSFIZZ_VST=OFF -DENABLE_LTO=OFF > /dev/null
  make -j"$(nproc)" sfizz_shared
  cd ../..
fi
echo "export VSCO_DIR=$PWD/VSCO-2-CE VSCO_SFZ_DIR=$PWD/vsco-sfz SSO_DIR=$PWD/sso SFIZZ_LIB=$PWD/sfizz/bs/library/lib/libsfizz.so"
