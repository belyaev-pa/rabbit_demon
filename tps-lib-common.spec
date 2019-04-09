Name:		tps-lib-common
Version:	0.1
Release:	0%{?dist}.sz
Summary:	Библиотека для взаимодействия с ТПС и ЛТПС
License:	commercial
URL:		http://src.fintech.ru
Source0:	tps-lib-common.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-XXXXXX)
BuildArch:	x86_64
Requires:	python2-pika python-kerberos 
#BuildRequires:	sqlite >= 3.7.0 glib2-devel postgresql-devel


%description
Библиотека для взаимодействия с ТПС и ЛТПС

%prep
# prepare before build
%setup -n %{name}  -q

%build
# build
exit 0

%pre
# before install 
exit 0

%post
# after install
#remove previous files
exit 0

%preun
# before uninstall

%postun
# after uninstall 

%install
# install

mkdir -p %{buildroot}/%{python_sitelib}/tps_lib_common/
cp -r ./lib/* %{buildroot}/%{python_sitelib}/tps_lib_common/


mkdir -p $RPM_BUILD_ROOT/usr/share/tps_lib_common/
cp -r ./share/* $RPM_BUILD_ROOT/usr/share/tps_lib_common/

%clean 
rm -rf %{buildroot}

%files
%defattr(644,root,root,-)
%attr(644,root,root) "%{python_sitelib}/tps_lib_common/"
%attr(644,root,root) "/usr/share/tps_lib_common/"

%exclude %{python_sitelib}/tps_lib_common/*.pyc
%exclude %{python_sitelib}/tps_lib_common/*.pyo
%exclude /usr/share/tps_lib_common/*.pyc
%exclude /usr/share/tps_lib_common/*.pyo



%changelog
* Tue Apr 9 2019 Deyneko Aleksey <deyneko@fintech.ru> 0.1-0
- Первый релиз 

