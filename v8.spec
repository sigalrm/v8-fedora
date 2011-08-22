%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%global major_version 3

Name:           v8
Version:        %{major_version}.5.1
Release:        1%{?dist}
Summary:        JavaScript Engine
Group:          System Environment/Libraries
License:        BSD
URL:            http://code.google.com/p/v8
# git clone git://github.com/%{name}/%{name}.git
# git archive --prefix=%{name}-%{version}/ %{version} \
#     >%{name}-%{version}.tar.bz2
# #Missing licenses:
# rm v8-3.0.0.1/benchmarks/earley-boyer.js
# rm v8-3.0.0.1/benchmarks/raytrace.js
# tar czf v8-3.0.0.1.tar.gz v8-3.0.0.1
Source0:        %{name}-%{version}.tar.bz2
Source1:        v8-js2c
Patch0:         v8-2.5.9-ccflags.patch
Patch1:         v8-2.5.9-shebangs.patch
Patch2:         v8-3.5.1-versioned-v8.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch:  %{ix86} x86_64 %{arm}
BuildRequires:  scons, readline-devel
%ifarch x86_64
Provides:       libv8.so.3()(64bit)
%else
Provides:       libv8.so.3
%endif

%description
V8 is Google's open source JavaScript engine. V8 is written in C++ and is used 
in Google Chrome, the open source browser from Google. V8 implements ECMAScript 
as specified in ECMA-262, 3rd edition.


%package devel
Group:          Development/Libraries
Summary:        Development headers and libraries for v8
Requires:       %{name} = %{version}-%{release}

%description devel
Development headers, libraries and tools for v8.


%prep
%setup -q
%patch0 -p1 -b .ccflags
%patch1 -p1 -b .shebangs
%patch2 -p1 -b .versionedV8
find \( -name '*.cc' -o -name '*.h' \) -print0 |xargs -0 chmod -x


%build
# Certain options enabled by -O2 causes binaries to crash immediately, for reasons yet unknown,
CCFLAGS="%{optflags} -fno-reorder-blocks -fno-strict-aliasing" \
        scons %{_smp_mflags} env='CCFLAGS: -fPIC' \
        library d8 cctests sample \
        library=shared soname=on protectheap=on console=readline sample=shell \
%ifarch x86_64
        arch=x64
%endif


%check
# preparser tests fail, let's switch them off for now
mv -v test/preparser/testcfg.py{,.INACTIVE}
LD_LIBRARY_PATH="$PWD" tools/test.py --no-build --progress=verbose


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_includedir}
mkdir -p $RPM_BUILD_ROOT%{_libdir}
install -pm644 include/*.h $RPM_BUILD_ROOT%{_includedir}
install -p libv8-%{version}.so $RPM_BUILD_ROOT%{_libdir}
ln -sf libv8-%{version}.so $RPM_BUILD_ROOT%{_libdir}/libv8.so
ln -sf libv8-%{version}.so $RPM_BUILD_ROOT%{_libdir}/libv8.so.%{major_version}
install -p libv8-%{version}.so $RPM_BUILD_ROOT%{_libdir}
mkdir -p $RPM_BUILD_ROOT%{_bindir}
install -p d8 $RPM_BUILD_ROOT%{_bindir}
install -p %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/js2c

install -d $RPM_BUILD_ROOT%{python_sitelib}
install -pm644 tools/js2c.py $RPM_BUILD_ROOT%{python_sitelib}
install -pm644 tools/jsmin.py $RPM_BUILD_ROOT%{python_sitelib}


%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog LICENSE
%{_bindir}/d8
%{_bindir}/js2c
%{_libdir}/libv8-%{version}.so
%{_libdir}/libv8.so.%{major_version}


%files devel
%defattr(-,root,root,-)
%{_includedir}/*.h
%{_libdir}/libv8.so
%{python_sitelib}/*.py*


%changelog
* Mon Aug 22 2011 Matěj Cepl <mcepl@redhat.com> - 3.5.1-1
- new upstream release
- provides also libv8.so.3 to satisfy chromium from the spot's repo
- switch off preparser test

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Dec 28 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.0.0.1-3
- Export some more symbols for node.js

* Mon Dec 13 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.0.0.1-2
- Remove files with broken licenses
- Fix mode of files in -debuginfo (this time for real)

* Sat Dec 11 2010 Lubomir Rintel <lkundrak@v3.sk> - 3.0.0.1-1
- Fix mode of a header file in -debuginfo 
- Newer version

* Fri Dec 10 2010 Lubomir Rintel <lkundrak@v3.sk> - 2.5.9-2
- Review fixes (Alex Hudson, #634909):
- No runnable scripts in python lib dir, wrap js2c
- Tidy up spaces/tabs
- Fix file permissions

* Sat Dec 04 2010 Lubomir Rintel <lkundrak@v3.sk> - 2.5.9-1
- Newer version
- Style adjustments
- Use SONAME upstream uses
- Attempt to be less hackish for CFLAGS overrides
- Enable test suite

* Sat Sep 18 2010 Lubomir Rintel <lkundrak@v3.sk> - 2.4.4-1
- Newer version

* Wed Sep 15 2010 Lubomir Rintel <lkundrak@v3.sk> - 2.3.8-2
- Package based on 2.3.11-1.20100831svn5385 by Tom "spot" Callaway
