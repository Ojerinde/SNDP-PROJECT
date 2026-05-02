#!/bin/bash
# Pre-downloads WUM products for all 6 PRIDE PPP-AR test cases.
# USAGE: bash /mnt/c/PPP_PROJECT/download_test_products.sh
#        Run once before:  bash test.sh
#
# WHY NEEDED:
#   pdp3.sh skips IGN FTP for GPS week < 2290 (all test dates are 2020-2023 = week < 2290).
#   Only Wuhan FTP is tried, which times out before completion.
#   This script uses IGN FTP directly (public, no auth) and Wuhan phasebias as fallback.
#
# SERVERS (same ones pdp3.sh uses, in priority order):
#   1. ftp://igs.ign.fr/pub/igs/products/mgex/{week}/  (IGN FTP - no auth)
#   2. ftp://igs.gnsswhu.cn/pub/whu/phasebias/{year}/{subdir}/  (Wuhan phasebias)

set -e
PRIDE_EXAMPLE="/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example"

download_product() {
    local url="" dest=""
    local fname=
    local dest_full="/"
    local dest_dec=""
    [ -f "" ] && echo "  skip  " && return 0
    mkdir -p ""
    echo "  get   "
    if wget --continue --tries=3 --timeout=120 -q -O "" "" 2>/dev/null && [ -s "" ]; then
        gunzip -f "" && return 0
    fi
    rm -f ""
    return 1
}

dl_date() {
    local year= doy= week=
    local ymd=""
    local dest="//product/common"
    echo "=== /  GPS week  ==="

    local ign="ftp://igs.ign.fr/pub/igs/products/mgex/"
    local whu_orb="ftp://igs.gnsswhu.cn/pub/whu/phasebias//orbit"
    local whu_clk="ftp://igs.gnsswhu.cn/pub/whu/phasebias//clock"
    local whu_bia="ftp://igs.gnsswhu.cn/pub/whu/phasebias//bias"

    # SP3 (orbit)
    download_product "/WUM0MGXRAP_0000_01D_05M_ORB.SP3.gz" "" ||
    download_product "/WUM0MGXRAP_0000_01D_05M_ORB.SP3.gz" "" ||
    echo "  FAILED: SP3"

    # CLK (clock)
    download_product "/WUM0MGXRAP_0000_01D_30S_CLK.CLK.gz" "" ||
    download_product "/WUM0MGXRAP_0000_01D_30S_CLK.CLK.gz" "" ||
    echo "  FAILED: CLK"

    # ERP (earth rotation)
    download_product "/WUM0MGXRAP_0000_01D_01D_ERP.ERP.gz" "" ||
    download_product "/WUM0MGXRAP_0000_01D_01D_ERP.ERP.gz" "" ||
    echo "  FAILED: ERP"

    # OSB.BIA (observable-specific biases)
    download_product "/WUM0MGXRAP_0000_01D_01D_OSB.BIA.gz" "" ||
    download_product "/WUM0MGXRAP_0000_01D_01D_OSB.BIA.gz" "" ||
    echo "  FAILED: OSB.BIA"
}

dl_date 2020 1   2086   # test 1 (static daily)
dl_date 2020 3   2086   # test 5 (troposphere estimation)
dl_date 2021 210 2168   # test 3+4 (kinematic 1-hour)
dl_date 2021 220 2170   # test 2 (kinematic daily)
dl_date 2023 1   2243   # test 6 MHM: needs previous day
dl_date 2023 2   2243   # test 6 (multipath)

echo ""
echo "Done. Run:  cd '/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example' && bash test.sh"