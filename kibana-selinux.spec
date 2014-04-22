%global modulename kibana
%global selinux_variants targeted
%global selinux_dirs /srv/www/kibana/src

Name            : kibana-selinux
Version         : 0.0.1
Release         : 1
Summary         : SELinux file contexts for Kibana
Group           : System Environment/Base

Source0         : %{modulename}.te
Source1         : %{modulename}.fc
Source2         : %{modulename}.if
URL             : https://github.com/bodgit/kibana-selinux
License         : BSD
Packager        : Matt Dainty <matt@bodgit-n-scarper.com>

BuildArch       : noarch
BuildRoot       : %{_tmppath}/%{name}-%{version}-root
Requires        : selinux-policy
Requires(post)  : /usr/sbin/semodule, /sbin/restorecon
Requires(postun): /usr/sbin/semodule, /sbin/restorecon
BuildRequires   : checkpolicy, selinux-policy-devel, hardlink

%description
SELinux file contexts for Kibana

%prep
%setup -cT
cp -p %{SOURCE0} %{SOURCE1} %{SOURCE2} .

%build
for selinuxvariant in %{selinux_variants}; do
    make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
    mv %{modulename}.pp %{modulename}.pp.${selinuxvariant}
    make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done

%install
rm -rf %{buildroot}

for selinuxvariant in %{selinux_variants}; do
    install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
    install -p -m 644 %{modulename}.pp.${selinuxvariant} \
        %{buildroot}%{_datadir}/selinux/${selinuxvariant}/%{modulename}.pp
done

# Consolidate multiple copies of the same file.
/usr/sbin/hardlink -cv %{buildroot}%{_datadir}/selinux

%clean
rm -rf %{buildroot}

%post
for selinuxvariant in %{selinux_variants}; do
    /usr/sbin/semodule -s ${selinuxvariant} -i \
        %{_datadir}/selinux/${selinuxvariant}/%{modulename}.pp &> /dev/null || :
done
for selinux_dir in %{selinux_dirs}; do
    [ -d ${selinux_dir} ] && /sbin/restorecon -R ${selinux_dir} &> /dev/null || :
done

%postun
if [ $1 -eq 0 ] ; then
    for selinuxvariant in %{selinux_variants}; do
        /usr/sbin/semodule -s ${selinuxvariant} -r %{modulename} &> /dev/null || :
    done
    for selinux_dir in %{selinux_dirs}; do
        [ -d ${selinux_dir} ] && /sbin/restorecon -R ${selinux_dir} &> /dev/null || :
    done
fi

%files
%defattr(-,root,root,0755)
%doc %{modulename}.*
%{_datadir}/selinux/*/%{modulename}.pp

%changelog
* Tue Apr 22 2014 Matt Dainty <matt@bodgit-n-scarper.com> 0.0.1-1
- Initial release.
