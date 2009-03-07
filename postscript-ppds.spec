%define version 2006
%define release %mkrel 5

##### RPM PROBLEM WORKAROUNDS

# Suppress automatically generated Requires for Perl libraries.
#define _requires_exceptions perl\(.*\)

#define _unpackaged_files_terminate_build       0 
#define _missing_doc_files_terminate_build      0


Summary: PPD files for PostScript printers
Name:		postscript-ppds
Version:	%{version}
Release:	%{release}
License:	Distributable
Group:		Publishing
URL:		http://cups.sourceforge.net/
BuildRequires:	cups-common
Requires:	foomatic-filters >= 3.0.2-1.20050802.1mdk ghostscript
BuildArchitectures: noarch

##### SOURCES

# CUPS-Drivers package from Sourceforge, only PPD files for native 
# PostScript printers used
Source200: 	ftp://cups.sourceforge.net/pub/cups/cups-drivers/0.3.6/cups-drivers-all-0.3.6.tar.bz2

# Perl script to clean up Manufacturer entries in the PPD files, so that
# drivers are sorted by the printer manufacturer in the graphical frontends
Source201: 	cleanppd.pl.bz2

# PPD file for a generic PostScript printer (taken from KUPS)
Source203: 	postscript.ppd.bz2

##### PATCHES

# Fix buggy PPD file
Patch200: cups-drivers-hplj5m_4.ppd.patch



##### BUILD ROOT

BuildRoot:	%_tmppath/%name-%version-%release-root



##### PACKAGE DESCRIPTION

%description
This package contains PPD files for older PostScript printers.

The PPD files for recent printers are in the foomatic-db package.

Setting up print queues with CUPS or foomatic-rip and these PPD files
makes all features of the printer available, therefore its use is
highly recommended. printerdrake will choose a manufacturer-supplied
PPD file automatically if one for your printer is found.



%prep
# remove old directory
rm -rf $RPM_BUILD_DIR/%{name}-%{version}
mkdir $RPM_BUILD_DIR/%{name}-%{version}

# PPD files for old PostScript printers
%setup -q -T -D -a 200 -n %{name}-%{version}

# Apply patch for buggy ppd file
%patch200 -p0

# Remove CUPS-O-MATIC PPDs
rm -rf cups-drivers-0.3.6/usr/share/cups/model/cups-o-matic

# Remove pstogstoraster-based PPD files, they do not work 
# when printing via Samba. There are other, better PPDs for 
# these printers.
rm -f cups-drivers-0.3.6/usr/share/cups/model/canon/bj10.ppd
rm -f cups-drivers-0.3.6/usr/share/cups/model/hp/djet_890c.ppd
rm -f cups-drivers-0.3.6/usr/share/cups/model/hp/laserjet_gs.ppd

# Remove CUPS PPD files, there are newer versions of them in the CUPS
# package
rm -f cups-drivers-0.3.6/usr/share/cups/model/hp/laserjet.ppd
rm -f cups-drivers-0.3.6/usr/share/cups/model/hp/deskjet.ppd



%build

# Nothing to build



%install

rm -rf $RPM_BUILD_ROOT

# Make directories
install -d $RPM_BUILD_ROOT%{_datadir}/cups/model

# Put the Sourceforge PPDs into CUPS PPD directory
cp -a cups-drivers-0.3.6/usr/share/cups/model/* $RPM_BUILD_ROOT%{_datadir}/cups/model/

# Install PPD file for a generic PostScript printer
bzcat %{SOURCE203} > $RPM_BUILD_ROOT%{_datadir}/cups/model/postscript.ppd

# Correct permissions of PPD file directory
chmod -R u+w,a+rX $RPM_BUILD_ROOT%{_datadir}/cups/model

# "cleanppd.pl" removes unwished PPD files (currently the ones for Birmy
# PowerRIP), fixes broken manufacturer entries, and cleans lines which
# contain only spaces and tabs.

# Uncompress Perl script for cleaning up the PPD files
bzcat %{SOURCE201} > ./cleanppd.pl
chmod a+rx ./cleanppd.pl
# Do the clean-up
find $RPM_BUILD_ROOT%{_datadir}/cups/model -name "*.ppd" -exec ./cleanppd.pl '{}' \;
# Remove PPDs which are not Adobe-compliant and therefore not working with
# CUPS 1.1.20
for ppd in `find $RPM_BUILD_ROOT%{_datadir}/cups/model -name "*.ppd.gz" -print`; do cupstestppd -q $ppd || (rm -f $ppd && echo "$ppd not Adobe-compliant. Deleted."); done



##### GENERAL STUFF

# Correct permissions for all documentation files
for f in %{buildroot}%{_datadir}/cups/model/*/*; do
  chmod a-x $f
done



##### FILES

%files
%defattr(-,root,root)
%{_datadir}/cups/model/*



# Restart the CUPS daemon when it is running, but do not start it when it
# is not running. The restart of the CUPS daemon updates the CUPS-internal
# PPD index

%post
/sbin/service cups condrestart > /dev/null 2>/dev/null || :

%postun
/sbin/service cups condrestart > /dev/null 2>/dev/null || :



%clean
rm -rf $RPM_BUILD_ROOT



