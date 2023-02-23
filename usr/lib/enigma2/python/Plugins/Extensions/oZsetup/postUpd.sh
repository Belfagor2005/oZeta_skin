#!/bin/sh
pyv="$(python -V 2>&1)"
echo "$pyv"
lulu='skin_templatepanelslulu.xml'
filename='/usr/share/enigma2/oZeta-FHD/skin.xml'
isInFile=$(cat $filename | grep -c $lulu)
echo "WAIT PLEASE..."

if [ -f /usr/share/enigma2/oZeta-FHD/zSkin/skin_templatepanelslulu.xml ];	then

    echo "skin_templatepanelslulu file exist"
    if [ $isInFile -eq 0 ]; then

        sed -i 's%</skin>%\t<include filename="zSkin/skin_templatepanelslulu.xml"/>\n</skin>%' $filename
        echo "skin.xml no content skin_templatepanelslulu.xml"
        echo "append skin_templatepanelslulu.xml to skin.xml"
        echo "done...  reboot please"
    else
        echo "skin.xml content skin_templatepanelslulu"
        echo "exit"

    fi
    echo ""

fi
echo ""

sleep 2;
rm -r /var/volatile/tmp/*.ipk > /dev/null 2>&1
rm -r /var/volatile/tmp/*.tar > /dev/null 2>&1
echo "*****************************************"
echo "*                                       *"
echo "*   oZeta skin options installed        *"
echo "*****************************************"

exit 0
