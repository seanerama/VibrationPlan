"""Known OS pattern library for rapidfuzz matching.

Each OSPattern represents an OS family.  The match_strings list contains
representative strings actually seen in RVTools and CloudPhysics exports.

Design philosophy:
- Include specific, well-known OS families with real-world string variants.
- Do NOT include vague descriptors like "Other Linux" or "Unknown" — those
  should produce low-confidence results so the classifier routes them to
  needs_info / needs_review tiers.
"""

from dataclasses import dataclass, field


@dataclass
class OSPattern:
    """A single OS family entry in the pattern library."""

    canonical_name: str  # Short display name, e.g. "Windows Server", "RHEL"
    vendor: str  # e.g. "Microsoft", "Red Hat", "Canonical"
    family: str  # Matches os_family values in the vme_matrix table
    match_strings: list[str] = field(default_factory=list)


OS_PATTERNS: list[OSPattern] = [
    # ── Microsoft Windows Server ────────────────────────────────────────────
    OSPattern(
        canonical_name="Windows Server",
        vendor="Microsoft",
        family="Windows Server",
        match_strings=[
            "Microsoft Windows Server 2025 (64-bit)",
            "Microsoft Windows Server 2022 (64-bit)",
            "Microsoft Windows Server 2019 (64-bit)",
            "Microsoft Windows Server 2016 (64-bit)",
            "Microsoft Windows Server 2012 R2 (64-bit)",
            "Microsoft Windows Server 2012 (64-bit)",
            "Microsoft Windows Server 2008 R2 (64-bit)",
            "Microsoft Windows Server 2008 (64-bit)",
            "Microsoft Windows Server 2003 (32-bit)",
            "Microsoft Windows Server 2003 (64-bit)",
            "Windows Server 2025",
            "Windows Server 2022",
            "Windows Server 2019",
            "Windows Server 2016",
            "Windows Server 2012 R2",
            "Windows Server 2012",
            "Windows Server 2008 R2",
            "Windows Server 2008",
            "Windows Server 2003",
            "Win Server",
            "WinServer",
        ],
    ),
    # ── Microsoft Windows Desktop ────────────────────────────────────────────
    OSPattern(
        canonical_name="Windows Desktop",
        vendor="Microsoft",
        family="Windows Desktop",
        match_strings=[
            "Microsoft Windows 11 (64-bit)",
            "Microsoft Windows 10 (64-bit)",
            "Microsoft Windows 10 (32-bit)",
            "Microsoft Windows 8.1 (64-bit)",
            "Microsoft Windows 8 (64-bit)",
            "Microsoft Windows 7 (64-bit)",
            "Microsoft Windows 7 (32-bit)",
            "Microsoft Windows Vista (64-bit)",
            "Microsoft Windows Vista (32-bit)",
            "Microsoft Windows XP Professional (32-bit)",
            "Microsoft Windows XP Professional (64-bit)",
            "Windows 11",
            "Windows 10",
            "Windows 8.1",
            "Windows 8",
            "Windows 7",
            "Windows Vista",
            "Windows XP",
            "Win 10",
            "Win 11",
        ],
    ),
    # ── Red Hat Enterprise Linux ─────────────────────────────────────────────
    OSPattern(
        canonical_name="RHEL",
        vendor="Red Hat",
        family="RHEL",
        match_strings=[
            "Red Hat Enterprise Linux 9 (64-bit)",
            "Red Hat Enterprise Linux 8 (64-bit)",
            "Red Hat Enterprise Linux 7 (64-bit)",
            "Red Hat Enterprise Linux 6 (64-bit)",
            "Red Hat Enterprise Linux 5 (64-bit)",
            "Red Hat Enterprise Linux 9",
            "Red Hat Enterprise Linux 8",
            "Red Hat Enterprise Linux 7",
            "Red Hat Enterprise Linux 6",
            "RHEL 9",
            "RHEL 8",
            "RHEL 7",
            "RHEL 6",
            "Red Hat Linux",
            "Red Hat Enterprise Linux",
        ],
    ),
    # ── Ubuntu ───────────────────────────────────────────────────────────────
    OSPattern(
        canonical_name="Ubuntu",
        vendor="Canonical",
        family="Ubuntu",
        match_strings=[
            "Ubuntu Linux (64-bit)",
            "Ubuntu Linux (32-bit)",
            "Ubuntu 24.04 LTS (64-bit)",
            "Ubuntu 22.04 LTS (64-bit)",
            "Ubuntu 22.04 LTS",
            "Ubuntu 20.04 LTS (64-bit)",
            "Ubuntu 20.04 LTS",
            "Ubuntu 18.04 (64-bit)",
            "Ubuntu 18.04",
            "Ubuntu 16.04 LTS",
            "Ubuntu 24.04",
            "Ubuntu 22.04",
            "Ubuntu 20.04",
            "Ubuntu Linux",
            "Ubuntu",
        ],
    ),
    # ── SUSE Linux Enterprise Server ─────────────────────────────────────────
    OSPattern(
        canonical_name="SLES",
        vendor="SUSE",
        family="SLES",
        match_strings=[
            "SUSE Linux Enterprise 15 (64-bit)",
            "SUSE Linux Enterprise 12 (64-bit)",
            "SUSE Linux Enterprise Server 15",
            "SUSE Linux Enterprise Server 12",
            "SUSE Linux Enterprise Server 15 SP4",
            "SUSE Linux Enterprise Server 12 SP5",
            "SLES 15",
            "SLES 12",
            "SUSE Linux Enterprise",
            "SUSE Enterprise Linux",
            "OpenSUSE Leap",
            "openSUSE",
        ],
    ),
    # ── CentOS ───────────────────────────────────────────────────────────────
    OSPattern(
        canonical_name="CentOS",
        vendor="CentOS",
        family="CentOS",
        match_strings=[
            "CentOS 8 (64-bit)",
            "CentOS 7 (64-bit)",
            "CentOS 7 (32-bit)",
            "CentOS Linux 8 (64-bit)",
            "CentOS Linux 7 (64-bit)",
            "CentOS Linux 7",
            "CentOS Linux 8",
            "CentOS 8",
            "CentOS 7",
            "CentOS",
        ],
    ),
    # ── Oracle Linux ──────────────────────────────────────────────────────────
    OSPattern(
        canonical_name="Oracle Linux",
        vendor="Oracle",
        family="Oracle Linux",
        match_strings=[
            "Oracle Linux 9 (64-bit)",
            "Oracle Linux 8 (64-bit)",
            "Oracle Linux 7 (64-bit)",
            "Oracle Linux 9",
            "Oracle Linux 8",
            "Oracle Linux 7",
            "Oracle Enterprise Linux",
            "Oracle Linux",
        ],
    ),
    # ── Debian ────────────────────────────────────────────────────────────────
    OSPattern(
        canonical_name="Debian",
        vendor="Debian",
        family="Debian",
        match_strings=[
            "Debian GNU/Linux 12 (64-bit)",
            "Debian GNU/Linux 11 (64-bit)",
            "Debian GNU/Linux 10 (64-bit)",
            "Debian GNU/Linux 12",
            "Debian GNU/Linux 11",
            "Debian GNU/Linux 10",
            "Debian 12",
            "Debian 11",
            "Debian 10",
            "Debian Linux",
            "Debian",
        ],
    ),
    # ── Fedora ───────────────────────────────────────────────────────────────
    OSPattern(
        canonical_name="Fedora",
        vendor="Fedora",
        family="Fedora",
        match_strings=[
            "Fedora Linux (64-bit)",
            "Fedora Linux 40 (64-bit)",
            "Fedora Linux 39 (64-bit)",
            "Fedora Linux 38 (64-bit)",
            "Fedora Linux 37 (64-bit)",
            "Fedora Linux 40",
            "Fedora Linux 39",
            "Fedora Linux",
            "Fedora 40",
            "Fedora 39",
            "Fedora",
        ],
    ),
    # ── VDI: Citrix ──────────────────────────────────────────────────────────
    OSPattern(
        canonical_name="Citrix Virtual Apps",
        vendor="ISV",
        family="Citrix Virtual Apps",
        match_strings=[
            "Citrix Virtual Apps",
            "Citrix Virtual Apps and Desktops",
            "Citrix XenApp",
            "Citrix XenDesktop",
            "Citrix DaaS",
            "Citrix",
        ],
    ),
    # ── VDI: Omnissa / VMware Horizon ────────────────────────────────────────
    OSPattern(
        canonical_name="Omnissa Horizon",
        vendor="ISV",
        family="Omnissa Horizon",
        match_strings=[
            "Omnissa Horizon",
            "VMware Horizon",
            "VMware Horizon View",
            "Horizon View",
            "Horizon Client",
        ],
    ),
    # ── VDI: HP Anyware ──────────────────────────────────────────────────────
    OSPattern(
        canonical_name="HP Anyware",
        vendor="ISV",
        family="HP Anyware",
        match_strings=[
            "HP Anyware",
            "Teradici PCoIP",
            "PCoIP",
            "HP Remote Workstation",
        ],
    ),
    # ── Legacy / Not Supported ──────────────────────────────────────────────
    OSPattern(
        canonical_name="DOS",
        vendor="Generic",
        family="DOS",
        match_strings=[
            "MS-DOS",
            "MS DOS",
            "DOS",
            "FreeDOS",
        ],
    ),
    OSPattern(
        canonical_name="OS/2",
        vendor="IBM",
        family="OS/2",
        match_strings=[
            "OS/2",
            "IBM OS/2",
            "OS2",
        ],
    ),
    OSPattern(
        canonical_name="NetWare",
        vendor="Novell",
        family="NetWare",
        match_strings=[
            "Novell NetWare 6.x",
            "Novell NetWare 5.x",
            "Novell NetWare",
            "NetWare",
        ],
    ),
    # ── Other known OSes (not in VME matrix but recognizable) ───────────────
    OSPattern(
        canonical_name="FreeBSD",
        vendor="FreeBSD Project",
        family="FreeBSD",
        match_strings=[
            "FreeBSD (64-bit)",
            "FreeBSD (32-bit)",
            "FreeBSD 14",
            "FreeBSD 13",
            "FreeBSD",
        ],
    ),
    OSPattern(
        canonical_name="Solaris",
        vendor="Oracle",
        family="Solaris",
        match_strings=[
            "Solaris 11 (64-bit)",
            "Solaris 10 (64-bit)",
            "Oracle Solaris 11",
            "Oracle Solaris 10",
            "Solaris 11",
            "Solaris 10",
            "Solaris",
        ],
    ),
]
