#!/bin/bash
# Pre-downloads WUM products for all 6 PRIDE PPP-AR test cases.
# USAGE: bash /mnt/c/PPP_PROJECT/download_test_products.sh
# Run once before:  bash test.sh
#
# WHY NEEDED: pdp3.sh skips IGN FTP for GPS week <2290 (all test dates 2020-2023
# fall below that threshold). This script uses IGN FTP (public, no auth) and
# Wuhan phasebias as fallback - the same sources pdp3.sh itself uses.

PRIDE_EXAMPLE="/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example"

download_product() {
    local url="$1" dest="$2"
    local fname=$(basename "$url")
    local dest_full="$dest/$fname"
    local dest_dec="${dest_full%.gz}"
    [ -f "$dest_dec" ] && echo "  skip  $(basename "$dest_dec")" && return 0
    mkdir -p "$dest"
    echo "  get   $fname"
    local attempt
    for attempt in 1 2 3; do
        rm -f "$dest_full"   # always start clean (avoids corrupt partial + append)
        [ "$attempt" -gt 1 ] && echo "  retry $attempt/3 ..."
        wget --tries=1 --timeout=180 -q -O "$dest_full" "$url" 2>/dev/null
        # validate: non-empty AND structurally valid gz
        if [ -s "$dest_full" ] && gunzip -t "$dest_full" 2>/dev/null; then
            gunzip -f "$dest_full" && return 0
        fi
        rm -f "$dest_full"
    done
    return 1
}

dl_date() {
    local year=$1 doy=$2 week=$3
    local ymd="${year}$(printf '%03d' $doy)"
    local dest="${PRIDE_EXAMPLE}/${year}/product/common"
    echo "=== ${year}/$(printf '%03d' $doy)  GPS week ${week} ==="
    local ign="ftp://igs.ign.fr/pub/igs/products/mgex/${week}"
    local whu_mgex="ftp://igs.gnsswhu.cn/pub/gnss/products/mgex/${week}"
    local whu_orb="ftp://igs.gnsswhu.cn/pub/whu/phasebias/${year}/orbit"
    local whu_clk="ftp://igs.gnsswhu.cn/pub/whu/phasebias/${year}/clock"
    local whu_bia="ftp://igs.gnsswhu.cn/pub/whu/phasebias/${year}/bias"

    download_product "${ign}/WUM0MGXRAP_${ymd}0000_01D_05M_ORB.SP3.gz"  "$dest" ||
    download_product "${whu_mgex}/WUM0MGXRAP_${ymd}0000_01D_05M_ORB.SP3.gz" "$dest" ||
    download_product "${whu_orb}/WUM0MGXRAP_${ymd}0000_01D_05M_ORB.SP3.gz"  "$dest" ||
    echo "  FAILED: SP3"

    download_product "${ign}/WUM0MGXRAP_${ymd}0000_01D_30S_CLK.CLK.gz"  "$dest" ||
    download_product "${whu_mgex}/WUM0MGXRAP_${ymd}0000_01D_30S_CLK.CLK.gz" "$dest" ||
    download_product "${whu_clk}/WUM0MGXRAP_${ymd}0000_01D_30S_CLK.CLK.gz"  "$dest" ||
    echo "  FAILED: CLK"

    download_product "${ign}/WUM0MGXRAP_${ymd}0000_01D_01D_ERP.ERP.gz"  "$dest" ||
    download_product "${whu_mgex}/WUM0MGXRAP_${ymd}0000_01D_01D_ERP.ERP.gz" "$dest" ||
    download_product "${whu_orb}/WUM0MGXRAP_${ymd}0000_01D_01D_ERP.ERP.gz"  "$dest" ||
    echo "  FAILED: ERP"

    download_product "${ign}/WUM0MGXRAP_${ymd}0000_01D_01D_OSB.BIA.gz"  "$dest" ||
    download_product "${whu_mgex}/WUM0MGXRAP_${ymd}0000_01D_01D_OSB.BIA.gz" "$dest" ||
    download_product "${whu_bia}/WUM0MGXRAP_${ymd}0000_01D_01D_OSB.BIA.gz"  "$dest" ||
    echo "  FAILED: OSB.BIA"
}

dl_date 2020 1   2086   # test 1: static daily
dl_date 2020 3   2086   # test 5: troposphere estimation
dl_date 2021 210 2168   # test 3+4: kinematic 1-hour
dl_date 2021 220 2170   # test 2: kinematic daily
dl_date 2023 1   2243   # test 6: MHM previous day
dl_date 2023 2   2243   # test 6: multipath

echo ""
echo "Done. Run:  cd '/mnt/c/Program Files (x86)/PRIDE-PPPAR-master/example' && bash test.sh"
