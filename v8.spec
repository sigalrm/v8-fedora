# clang doesn't understand hardening, specifically "-specs="
%global clang_optflags %(echo %{optflags} | sed 's|-specs=/usr/lib/rpm/redhat/redhat-hardened-cc1||g')
%global clang_ldflags %(echo "%{__global_ldflags} -Wl,--build-id" | sed 's|-specs=/usr/lib/rpm/redhat/redhat-hardened-ld||g')

# Hi Googlers! If you're looking in here for patches, nifty.
# You (and everyone else) are welcome to use any of my Chromium spec files and
# patches under the terms of the GPLv2 or later.
# You (and everyone else) are welcome to use any of my V8-specific spec files
# and patches under the terms of the BSD license.
# You (and everyone else) may NOT use my spec files or patches under any other
# terms.
# I hate to be a party-pooper here, but I really don't want to help Google
# make a proprietary browser. There are enough of those already.
# All copyrightable work in these spec files and patches is Copyright 2011
# Tom Callaway <spot@fedoraproject.org>

# For the 1.2 branch, we use 0s here
# For 1.3+, we use the three digit versions
# Hey, now there are four digits. What do they mean? Popsicle.
# Now there are three digits. Yeah. HOW ABOUT DEM APPLES?!?
%global somajor 6
%global sominor 7
%global sobuild 17
%global sover %{somajor}

Name:		v8
Version:	%{somajor}.%{sominor}.%{sobuild}
Release:	4%{?dist}
Epoch:		1
Summary:	JavaScript Engine
Group:		System Environment/Libraries
License:	BSD
URL:		https://chromium.googlesource.com/v8/v8/
# To make the source, you need to have depot_tools installed and in your PATH
# https://chromium.googlesource.com/chromium/tools/depot_tools.git/+archive/7e7a454f9afdddacf63e10be48f0eab603be654e.tar.gz
# Note that the depot_tools tarball above does not unpack into its own directory.
# mkdir v8-tmp
# cd v8-tmp
# fetch v8
# cd v8
# git checkout 6.7.17
# gclient sync
# cd ..
# mv v8 v8-6.7.17
# tar -c  --exclude=.git --exclude=build/linux -J -f v8-6.7.17.tar.xz v8-6.7.17
Source0:	v8-6.7.17.tar.xz
# https://chromium.googlesource.com/chromium/tools/depot_tools.git/+archive/7e7a454f9afdddacf63e10be48f0eab603be654e.tar.gz
Source1:        depot_tools.git-master.tar.gz
# Taken from chromium-60.0.3112.78/build/linux/unbundle/icu.gn
Source2:	icu.gn
# Needed to build gn. :P
# git clone https://chromium.googlesource.com/chromium/src/base
# tar cvfj chromium-base-git2d35e4d.tar.bz2 base/
Source3:	chromium-base-git2d35e4d.tar.bz2
# git clone https://chromium.googlesource.com/chromium/src/tools/gn
# tar cvfj gn-source-gitf833e90.tar.bz2 gn/
Source4:	gn-source-gitf833e90.tar.bz2
# Patch0:		v8-4.10.91-system_icu.patch
# Patch2:		v8-5.2.258-bundled-binutils.patch
Patch3:		v8-5.2.258-gcc7.patch
Patch5:		v8-6.2.91-nolambda.patch
Patch6:		v8-6.2.91-sover.patch
# Patch7:		v8-6.2.91-noxlocale.patch
# do not assume we are cross compiling
# silly google
Patch8:		v8-6.7.17-notcross.patch
# On i686 and armv7hl, use -g1 to avoid mem exhaust
Patch9:		v8-6.7.17-i686-g1-to-avoid-mem-exhaust.patch
# Fedora 25 and older need less flags
# and clang is not tolerant of flags it doesn't know about
Patch10:	v8-6.2.91-oldclang-flags.patch
# Workaround gcc8 bug in gn
Patch11:	v8-6.2.91-gcc8-gn-fabi11.patch
# So many gcc fixes
Patch12:	v8-6.7.17-fixme.patch
# Use Fedora optflags
Patch13:	v8-6.7.17-optflags.patch
# Reconcile libc++abi with unwind.h from gcc
# https://bugs.llvm.org/show_bug.cgi?id=35945
# Modified patch from https://reviews.llvm.org/D42242
Patch14:        v8-6.7.17-fix-gcc-unwind-header.patch

# PPC64 doesn't like libcxx code.
# error: '(9.223372036854775807e+18 / 1.0e+9)' is not a constant expression
# aarch64 doesn't work either.
# code does not compile on s390
ExclusiveArch:	%{ix86} x86_64 %{arm} ppc mipsel mips64el
BuildRequires:	readline-devel, libicu-devel, ninja-build
BuildRequires:	python2-devel, glib2-devel, libatomic
# BuildRequires:	clang, llvm
BuildRequires:	gcc, gcc-c++

%description
V8 is Google's open source JavaScript engine. V8 is written in C++ and is used 
in Google Chrome, the open source browser from Google. V8 implements ECMAScript 
as specified in ECMA-262, 3rd edition.

%package devel
Group:		Development/Libraries
Summary:	Development headers and libraries for v8
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description devel
Development headers and libraries for v8.

%package -n python2-v8
%{?python_provide:%python_provide python2-v8}
# Remove before F30
Provides: %{name}-python = %{version}-%{release}
Provides: %{name}-python%{?_isa} = %{version}-%{release}
Obsoletes: %{name}-python < %{version}-%{release}
Summary:	Python libraries from v8
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description -n python2-v8
Python libraries from v8.

%prep
%setup -q -T -c -n depot_tools -a 1
%setup -q -n %{name}-%{version} -a 3
# %%patch0 -p1 -b .system_icu
# %%patch2 -p1 -b .bb
# %%patch3 -p1 -b .gcc7
%patch5 -p1 -b .nolambda
%patch6 -p1 -b .sover
# %%patch7 -p1 -b .noxlocale
%patch8 -p1 -b .notcross
%ifarch i686 armv7hl
%patch9 -p1 -b .memexhaust
%endif
%if 0%{?fedora} <= 25
%patch10 -p1 -b .oldflags
%endif

cp -a %{SOURCE2} third_party/icu/BUILD.gn

pushd tools
tar xvf %{SOURCE4}
popd

%patch11 -p1 -b .fabi11
%patch12 -p1 -b .fixme
%patch13 -p1 -b .optflags
%patch14 -p1 -b .unwind

SPLITOPTFLAGS=""
for i in `echo %{optflags} | sed 's/ /\n/g'`; do
	SPLITOPTFLAGS+="\"$i\", "
done
export SPLITOPTFLAGS

SPLITLDFLAGS=""
for j in `echo %{build_ldflags} | sed 's/ /\n/g'`; do
	SPLITLDFLAGS+="\"$j\", "
done
export SPLITLDFLAGS

sed -i "s|\"\$OPTFLAGS\"|$SPLITOPTFLAGS|g" build/config/compiler/BUILD.gn
sed -i "s|\"\$OPTLDFLAGS\"|$SPLITLDFLAGS|g" build/config/compiler/BUILD.gn

# Use system header ... except it doesn't work.
# rm -rf src/third_party/valgrind/valgrind.h
# ln -s /usr/include/valgrind/valgrind.h src/third_party/valgrind/valgrind.h

# Don't make thin libraries. :(
for i in `find . -type f -name '*.mk'`; do sed -i 's|alink_thin|alink|g' $i; done
sed -i "s|'alink_thin'|'alink'|g" tools/gyp/pylib/gyp/generator/make.py
sed -i "s|'alink_thin'|'alink'|g" tools/gyp/pylib/gyp/generator/ninja.py
# sed -i "s|crsT|crs|g" out/Makefile
sed -i "s|crsT|crs|g" tools/gyp/pylib/gyp/generator/make.py


rm -rf third_party/binutils/Linux_x64/Release/bin/ld.gold
rm -rf third_party/llvm-build/Release+Asserts
mkdir -p third_party/llvm-build/Release+Asserts/bin
pushd third_party/llvm-build/Release+Asserts/bin
ln -s /usr/bin/clang clang
ln -s /usr/bin/clang++ clang++
ln -s /usr/bin/llvm-ar llvm-ar
popd

for i in `grep -rl "Wno-undefined-var-template" *`; do
	sed -i 's|-Wno-undefined-var-template||g' $i
done

%build
%ifarch x86_64
%global v8arch x64
%endif
%ifarch %{ix86}
%global v8arch x86
%endif
%ifarch %{arm}
%global v8arch arm
%endif
%ifarch aarch64
%global v8arch arm64
%endif
%ifarch mipsel
%global v8arch mipsel
%endif
%ifarch mips64el
%global v8arch mips64el
%endif
%ifarch ppc
%global v8arch ppc
%endif
%ifarch ppc64
%global v8arch ppc64
%endif
%ifarch s390
%global v8arch s390
%endif
%ifarch s390x
%global v8arch s390x
%endif

# DO THE HARLEM SHAKE
# err... I mean, build gn from source.
pushd tools/gn
./bootstrap/bootstrap.py -s
popd
rm -rf buildtools/linux64/gn*
# the tooling thinks all linux is "linux64"
cp -a out/Release/gn buildtools/linux64/gn

# Replace ninja in depot_tools
rm -rf ../depot_tools/ninja
ln -s /usr/bin/ninja ../depot_tools/ninja

V8_GN_DEFINES=""
V8_GN_DEFINES+=' use_sysroot=false use_gold=false enable_nacl=false linux_use_bundled_binutils=false is_component_build=true clang_use_chrome_plugins=false'
V8_GN_DEFINES+=' libcpp_is_static=true v8_use_external_startup_data=false'
V8_GN_DEFINES+=' v8_target_cpu="%{v8arch}"'
V8_GN_DEFINES+=' is_clang=false'
%ifarch armv7hl armv7hnl
V8_GN_DEFINES+=' arm_float_abi="hard"'
%endif
%ifarch armv5tel armv6l armv7l
V8_GN_DEFINES+=' arm_float_abi="softfp"'
%endif

export PATH=$PATH:%{_builddir}/depot_tools
CHROMIUM_BUILDTOOLS_PATH=./buildtools/ gn gen out.gn/%{v8arch}.release --args="$V8_GN_DEFINES"
mkdir -p out.gn/%{v8arch}.release/gen/shim_headers/icui18n_shim/third_party/icu/source/i18n/unicode
mkdir -p out.gn/%{v8arch}.release/gen/shim_headers/icuuc_shim/third_party/icu/source/common/unicode
../depot_tools/ninja -vvv -C out.gn/%{v8arch}.release

%install
pushd out.gn/%{v8arch}.release
# library first
mkdir -p %{buildroot}%{_libdir}
cp -a libv8*.so.%{somajor} %{buildroot}%{_libdir}
# Next, binaries
mkdir -p %{buildroot}%{_bindir}
install -p -m0755 d8 %{buildroot}%{_bindir}
install -p -m0755 mksnapshot %{buildroot}%{_bindir}
# install -p -m0755 parser_fuzzer %{buildroot}%{_bindir}
%if 0
# BLOBS! (Don't stress. They get built out of source code.)
install -p -m0644 natives_blob.bin snapshot_blob.bin %{buildroot}%{_libdir}
%endif
popd

# Now, headers
mkdir -p %{buildroot}%{_includedir}
install -p -m0644 include/*.h %{buildroot}%{_includedir}
cp -a include/libplatform %{buildroot}%{_includedir}
# Are these still useful?
mkdir -p %{buildroot}%{_includedir}/v8/extensions/
install -p -m0644 src/extensions/*.h %{buildroot}%{_includedir}/v8/extensions/

# Make shared library links
pushd %{buildroot}%{_libdir}
ln -sf libv8.so.%{somajor} libv8.so
ln -sf libv8_libplatform.so.%{somajor} libv8_libplatform.so
ln -sf libv8_libbase.so.%{somajor} libv8_libbase.so
popd

# install Python JS minifier scripts for nodejs
install -d %{buildroot}%{python_sitelib}
sed -i 's|/usr/bin/python2.4|/usr/bin/env python|g' tools/jsmin.py
sed -i 's|/usr/bin/python2.4|/usr/bin/env python|g' tools/js2c.py
install -p -m0744 tools/jsmin.py %{buildroot}%{python_sitelib}/
install -p -m0744 tools/js2c.py %{buildroot}%{python_sitelib}/
chmod -R -x %{buildroot}%{python_sitelib}/*.py*

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license LICENSE
%doc AUTHORS ChangeLog
%{_bindir}/d8
%{_bindir}/mksnapshot
%{_libdir}/*.so.*
%if 0
%{_libdir}/*.bin
%endif

%files devel
%{_includedir}/*.h
%{_includedir}/libplatform/
%dir %{_includedir}/v8/
%{_includedir}/v8/extensions/
%{_libdir}/*.so

%files -n python2-v8
%{python_sitelib}/j*.py*

%changelog
* Tue May 15 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1:6.7.17-4
- Add libv8_libbase.so symlink to devel package.

* Tue May 8 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1:6.7.17-3
- Fix ARM build. Integrate fix for https://bugs.llvm.org/show_bug.cgi?id=35945

* Mon Apr 30 2018 Pete Walter <pwalter@fedoraproject.org> - 1:6.7.17-2
- Rebuild for ICU 61.1

* Wed Mar 14 2018 Tom Callaway <spot@fedoraproject.org> - 1:6.7.17-1
- update to 6.7.17

* Wed Mar 07 2018 Adam Williamson <awilliam@redhat.com> - 1:6.2.91-8
- Rebuild to fix GCC 8 mis-compilation
  See https://da.gd/YJVwk ("GCC 8 ABI change on x86_64")

* Mon Feb 19 2018 Tom Callaway <spot@fedoraproject.org> - 1:6.2.91-7
- fix platform library symlink

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:6.2.91-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Nov 30 2017 Pete Walter <pwalter@fedoraproject.org> - 1:6.2.91-5
- Rebuild for ICU 60.1

* Thu Aug 31 2017 Tom Callaway <spot@fedoraproject.org> - 1:6.2.91-4
- disable some cflags on fedora 25 or older

* Sun Aug 20 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1:6.2.91-3
- Add Provides for the old name without %%_isa

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1:6.2.91-2
- Python 2 binary package renamed to python2-v8
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Mon Jul 31 2017 Tom Callaway <spot@fedoraproject.org> - 1:6.2.91-1
- 6.2.91

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.2.258-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Mar  1 2017 Tom Callaway <spot@fedoraproject.org> - 1:5.2.258-11
- fix ppc64 build

* Tue Feb 28 2017 Tom Callaway <spot@fedoraproject.org> - 1:5.2.258-10
- fix ftbfs (thanks to Ben Noordhuis)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.2.258-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Igor Gnatenko <ignatenko@redhat.com> - 1:5.2.258-8
- Rebuild for readline 7.x

* Mon Oct 17 2016 Tom Callaway <spot@fedoraproject.org> - 1:5.2.258-7
- force v8 not to make thin libraries

* Thu Oct 13 2016 Tom Callaway <spot@fedoraproject.org> - 1:5.2.258-6
- use smaller, better compressed source tarball without unnecessary git bits

* Mon Oct 10 2016 Tom Callaway <spot@fedoraproject.org> - 1:5.2.258-5
- add bundledbinutils option to Makefile to disable "thin" static libs

* Mon Sep 26 2016 Tom Callaway <spot@fedoraproject.org> - 1:5.2.258-4
- set snapshot=external to enable blob creation
- include blobs, static libraries

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:5.2.258-3
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri May 13 2016 Tom Callaway <spot@fedoraproject.org> - 1:5.2.258-2
- build with optflags, except for the hardening script which clang has no idea what to do with

* Mon May  9 2016 Tom Callaway <spot@fedoraproject.org> - 1:5.2.258-1
- update to 5.2.258

* Mon May  2 2016 Tom Callaway <spot@fedoraproject.org> - 1:5.2.197-1
- update to 5.2.197
- WELCOME TO THE WORLD OF TOMORROW

* Fri Apr 15 2016 David Tardon <dtardon@redhat.com> - 1:3.14.5.10-24
- rebuild for ICU 57.1

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:3.14.5.10-23
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Oct 28 2015 David Tardon <dtardon@redhat.com> - 1:3.14.5.10-22
- rebuild for ICU 56.1

* Mon Sep 21 2015 Tom Callaway <spot@fedoraproject.org> - 1:3.14.5.10-21
- add REPLACE_INVALID_UTF8 code needed for nodejs

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.14.5.10-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun  8 2015 Tom Callaway <spot@fedoraproject.org> - 1:3.14.5.10-19
- split off python subpackage (bz 959145)

* Thu Apr 23 2015 Tom Callaway <spot@fedoraproject.org> - 1:3.14.5.10-18
- backport security fix for ARM - CVE-2014-3152

* Thu Feb 19 2015 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-17
- backports for nodejs 0.10.36

* Mon Jan 26 2015 David Tardon <dtardon@redhat.com> - 1:3.14.5.10-16
- rebuild for ICU 54.1

* Tue Dec  2 2014 Tom Callaway <spot@fedoraproject.org> - 1:3.14.5.10-15
- use system valgrind header (bz1141483)

* Wed Sep 17 2014 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-14
- backport bugfix that eliminates unused-local-typedefs warning
- backport security fix: Fix Hydrogen bounds check elimination (CVE-2013-6668; RHBZ#1086120)
- backport fix to segfault caused by the above patch

* Tue Aug 26 2014 David Tardon <dtardon@redhat.com> - 1:3.14.5.10-13
- rebuild for ICU 53.1

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.14.5.10-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 31 2014 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-11
- backport security fix for memory corruption and stack overflow (RHBZ#1125464)
  https://groups.google.com/d/msg/nodejs/-siJEObdp10/2xcqqmTHiEMJ
- backport bug fix for x64 MathMinMax for negative untagged int32 arguments.
  https://github.com/joyent/node/commit/3530fa9cd09f8db8101c4649cab03bcdf760c434

* Thu Jun 19 2014 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-10
- fix corner case in integer comparisons (v8 bug#2416; nodejs bug#7528)

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.14.5.10-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat May 03 2014 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-8
- use clock_gettime() instead of gettimeofday(), which increases V8 performance
  dramatically on virtual machines

* Tue Mar 18 2014 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-7
- backport fix for unsigned integer arithmetic (RHBZ#1077136; CVE-2014-1704)

* Mon Feb 24 2014 Tomas Hrcka <thrcka@redhat.com> - 1:3.14.5.10-6
- Backport fix for incorrect handling of popular pages (RHBZ#1059070; CVE-2013-6640)

* Fri Feb 14 2014 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-5
- rebuild for icu-52

* Mon Jan 27 2014 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-4
- backport fix for enumeration for objects with lots of properties

* Fri Dec 13 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-3
- backport fix for out-of-bounds read DoS (RHBZ#1039889; CVE-2013-6640)

* Fri Aug 02 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-2
- backport fix for remote DoS or unspecified other impact via type confusion
  (RHBZ#991116; CVE-2013-2882)

* Wed May 29 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.10-1
- new upstream release 3.14.5.10

* Mon May 06 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1:3.14.5.8-2
- Fix ownership of include directory (#958729)

* Fri Mar 22 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.14.5.8-1
- new upstream release 3.14.5.8
- backport security fix for remote DoS via crafted javascript (RHBZ#924495; CVE-2013-2632)

* Mon Mar 11 2013 Stephen Gallagher <sgallagh@redhat.com> - 1:3.14.5.7-3
- Update to v8 3.14.5.7 for Node.js 0.10.0

* Sat Jan 26 2013 T.C. Hollingsworth <tchollingsworth@gmail.com> - 1:3.13.7.5-2
- rebuild for icu-50
- ignore new GCC 4.8 warning

* Tue Dec  4 2012 Tom Callaway <spot@fedoraproject.org> - 1:3.13.7.5-1
- update to 3.13.7.5 (needed for chromium 23)
- Resolves multiple security issues (CVE-2012-5120, CVE-2012-5128)
- d8 is now using a static libv8, resolves bz 881973)

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.10.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul  6 2012 Tom Callaway <spot@fedoraproject.org> 1:3.10.8-1
- update to 3.10.8 (chromium 20)

* Tue Jun 12 2012 Tom Callaway <spot@fedoraproject.org> 1:3.9.24-1
- update to 3.9.24 (chromium 19)

* Mon Apr 23 2012 Thomas Spura <tomspur@fedoraproject.org> 1:3.7.12.6
- rebuild for icu-49

* Fri Mar 30 2012 Dennis Gilmore <dennis@ausil.us> 1:3.7.12-5
- make sure the right arm abi is used in the second call of scons

* Thu Mar 29 2012 Dennis Gilmore <dennis@ausil.us> 1:3.7.12-4
- use correct arm macros
- use the correct abis for hard and soft float

* Tue Mar 20 2012 Tom Callaway <spot@fedoraproject.org> 3.7.12-3
- merge changes from Fedora spec file, sync, add epoch

* Fri Feb 17 2012 Tom Callaway <spot@fedoraproject.org> 3.7.12-2
- add -Wno-error=strict-overflow for gcc 4.7 (hack, hack, hack)

* Mon Feb 13 2012 Tom Callaway <spot@fedoraproject.org> 3.7.12-1
- update to 3.7.12

* Thu Nov  3 2011 Tom Callaway <spot@fedoraproject.org> 3.5.10-1
- update to 3.5.10

* Mon Sep 26 2011 Tom Callaway <spot@fedoraproject.org> 3.4.14-2
- final 3.4.14 tag
- include JavaScript minifier scripts in -devel

* Fri Jun 10 2011 Tom Callaway <spot@fedoraproject.org> 3.2.10-1
- tag 3.2.10

* Thu Apr 28 2011 Tom Callaway <spot@fedoraproject.org> 3.1.8-1
- "stable" v8 match for "stable" chromium (tag 3.1.8)

* Tue Feb 22 2011 Tom Callaway <spot@fedoraproject.org> 3.1.5-1.20110222svn6902
- update to 3.1.5
- enable experimental i18n icu stuff for chromium

* Tue Jan 11 2011 Tom Callaway <spot@fedoraproject.org> 3.0.7-1.20110111svn6276
- update to 3.0.7

* Tue Dec 14 2010 Tom "spot" Callaway <tcallawa@redhat.com> 3.0.0-2.20101209svn5957
- fix sloppy code where NULL is used

* Thu Dec  9 2010 Tom "spot" Callaway <tcallawa@redhat.com> 3.0.0-1.20101209svn5957
- update to 3.0.0

* Fri Oct 22 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.5.1-1.20101022svn5692
- update to 2.5.1
- fix another fwrite with no return checking case

* Thu Oct 14 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.5.0-1.20101014svn5625
- update to 2.5.0

* Mon Oct  4 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.4.8-1.20101004svn5585
- update to 2.4.8

* Tue Sep 14 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.4.3-1.20100914svn5450
- update to 2.4.3

* Tue Aug 31 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.11-1.20100831svn5385
- update to svn5385

* Fri Aug 27 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.11-1.20100827svn5365
- update to 2.3.11, svn5365

* Tue Aug 24 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.10-1.20100824svn5332
- update to 2.3.10, svn5332

* Wed Aug 18 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.9-1.20100819svn5308
- update to 2.3.9, svn5308

* Wed Aug 11 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.7-1.20100812svn5251
- update to svn5251

* Wed Aug 11 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.7-1.20100811svn5248
- update to 2.3.7, svn5248

* Tue Aug 10 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.6-1.20100809svn5217
- update to 2.3.6, svn5217

* Fri Aug  6 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.5-1.20100806svn5198
- update to 2.3.5, svn5198

* Mon Jul 26 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.3-1.20100726svn5134
- update to 2.3.3, svn5134

* Fri Jul 16 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.3.0-1.20100716svn5088
- update to 2.3.0, svn5088

* Tue Jul  6 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.22-1.20100706svn5023
- update to 2.2.22, svn5023

* Fri Jul  2 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.21-1.20100702svn5010
- update to svn5010

* Wed Jun 30 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.21-1.20100630svn4993
- update to 2.2.21, svn4993
- include checkout script

* Thu Jun  3 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.14-1.20100603svn4792
- update to 2.2.14, svn4792

* Tue Jun  1 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.13-1.20100601svn4772
- update to 2.2.13, svn4772

* Thu May 27 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.12-1.20100527svn4747
- update to 2.2.12, svn4747

* Tue May 25 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.11-1.20100525svn4718
- update to 2.2.11, svn4718

* Thu May 20 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.10-1.20100520svn4684
- update to svn4684

* Mon May 17 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.10-1.20100517svn4664
- update to 2.2.10, svn4664

* Thu May 13 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.9-1.20100513svn4653
- update to svn4653

* Mon May 10 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.9-1.20100510svn4636
- update to 2.2.9, svn4636

* Tue May  4 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.7-1.20100504svn4581
- update to 2.2.7, svn4581

* Mon Apr 19 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.3-1.20100419svn4440
- update to 2.2.3, svn4440

* Tue Apr 13 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.2-1.20100413svn4397
- update to 2.2.2, svn4397

* Thu Apr  8 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.1-1.20100408svn4359
- update to 2.2.1, svn4359

* Mon Mar 29 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.2.0-1.20100329svn4309
- update to 2.2.0, svn4309

* Thu Mar 25 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.1.8-1.20100325svn4273
- update to 2.1.8, svn4273

* Mon Mar 22 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.1.5-1.20100322svn4204
- update to 2.1.5, svn4204

* Mon Mar 15 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.1.4-1.20100315svn4129
- update to 2.1.4, svn4129

* Wed Mar 10 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.1.0-1.20100310svn4088
- update to 2.1.3, svn4088

* Thu Feb 18 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.1.0-1.20100218svn3902
- update to 2.1.0, svn3902

* Fri Jan 22 2010 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.6-1.20100122svn3681
- update to 2.0.6, svn3681

* Tue Dec 29 2009 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.5-1.20091229svn3528
- svn3528

* Mon Dec 21 2009 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.5-1.20091221svn3511
- update to 2.0.5, svn3511

* Wed Dec  9 2009 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.3-1.20091209svn3443
- update to 2.0.3, svn3443

* Tue Nov 24 2009 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.2-1.20091124svn3353
- update to 2.0.2, svn3353

* Wed Nov 18 2009 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.0-1.20091118svn3334
- update to 2.0.0, svn3334

* Tue Oct 27 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.16-1.20091027svn3152
- update to 1.3.16, svn3152

* Tue Oct 13 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.15-1.20091013svn3058
- update to svn3058

* Thu Oct  8 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.15-1.20091008svn3036
- update to 1.3.15, svn3036

* Tue Sep 29 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.13-1.20090929svn2985
- update to svn2985
- drop unused parameter patch, figured out how to work around it with optflag mangling
- have I mentioned lately that scons is garbage?

* Mon Sep 28 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.13-1.20090928svn2980
- update to 1.3.13, svn2980

* Wed Sep 16 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.11-1.20090916svn2903
- update to 1.3.11, svn2903

* Wed Sep  9 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.9-1.20090909svn2862
- update to 1.3.9, svn2862

* Thu Aug 27 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.8-1.20090827svn2777
- update to 1.3.8, svn2777

* Mon Aug 24 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.6-1.20090824svn2747
- update to 1.3.6, svn2747

* Tue Aug 18 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.4-1.20090818svn2708
- update to svn2708, build and package d8

* Fri Aug 14 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.4-1.20090814svn2692
- update to 1.3.4, svn2692

* Wed Aug 12 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.3-1.20090812svn2669
- update to 1.3.3, svn2669

* Mon Aug 10 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.2-1.20090810svn2658
- update to svn2658

* Fri Aug  7 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.2-1.20090807svn2653
- update to svn2653

* Wed Aug  5 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.2-1.20090805svn2628
- update to 1.3.2, svn2628

* Mon Aug  3 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.1-1.20090803svn2607
- update to svn2607

* Fri Jul 31 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.1-1.20090731svn2602
- update to svn2602

* Thu Jul 30 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.1-1.20090730svn2592
- update to 1.3.1, svn 2592

* Mon Jul 27 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.0-1.20090727svn2543
- update to 1.3.0, svn 2543

* Fri Jul 24 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.14-1.20090724svn2534
- update to svn2534

* Mon Jul 20 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.14-1.20090720svn2510
- update to svn2510

* Thu Jul 16 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.14-1.20090716svn2488
- update to svn2488

* Wed Jul 15 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.14-1.20090715svn2477
- update to 1.2.14, svn2477

* Mon Jul 13 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.13-1.20090713svn2434
- update to svn2434

* Sat Jul 11 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.13-1.20090711svn2430
- update to 1.2.13, svn2430

* Wed Jul  8 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.12-1.20090708svn2391
- update to 1.2.12, svn2391

* Sat Jul  4 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.11-1.20090704svn2356
- update to 1.2.11, svn2356

* Fri Jun 26 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.9-1.20090626svn2284
- update to svn2284

* Wed Jun 24 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.9-1.20090624svn2262
- update to 1.2.9, svn2262

* Thu Jun 18 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.7-2.20090618svn2219
- fix unused-parameter patch

* Thu Jun 18 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.7-1.20090618svn2219
- update to 1.2.8, svn2219

* Mon Jun 8 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.7-2.20090608svn2123
- fix gcc44 compile for Fedora 11

* Mon Jun  8 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.7-1.20090608svn2123
- update to 1.2.7, svn2123

* Thu May 28 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.2.5-1.20090528svn2072
- update to newer svn checkout

* Sun Feb 22 2009 Tom "spot" Callaway <tcallawa@redhat.com> 1.0.1-1.20090222svn1332
- update to newer svn checkout

* Sun Sep 14 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.2-2.20080914svn300
- make a versioned shared library properly

* Sun Sep 14 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.2-1.20080914svn300
- Initial package for Fedora

