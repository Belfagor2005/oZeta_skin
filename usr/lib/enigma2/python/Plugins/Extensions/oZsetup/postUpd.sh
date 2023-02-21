#!/bin/sh
# <!-- **************************************  -->
# <!-- Install option skin oZeta-FHD by mmark  -->
# <!-- Don't Remove this Disclaimer            -->
# <!-- **************************************  -->

lulu='skin_templatepanelslulu'
filename='/usr/share/enigma2/oZeta-FHD/skin.xml'
isInFile=$(cat $filename | grep -c $lulu)

if [ ! -d /usr/share/enigma2/oZeta-FHD ]; then
	echo "skin ozeta not present"
else
	echo "SKIN OZETA PRESENT"  
	if [ -f /usr/share/enigma2/oZeta-FHD/skin_templatepanelslulu ];	then
		echo "file exist"

		if [ $isInFile -eq 0 ]; then
			sed -i 's%</skin>%\t<include filename="zSkin/skin_templatepanelslulu.xml"/>\n</skin>%' $filename
			echo "no content"
		else
			echo "content"

		fi

	# if [ $isInFile -eq 0 ]; then
		# sed -i 's%</skin>%\t<include filename="zSkin/skin_templatepanelslulu.xml"/>\n</skin>%' $filename
		# echo "no content"
	# else
		# echo "content"
	fi 
fi
	
sleep 2
rm -r /var/volatile/tmp/*.ipk > /dev/null 2>&1
rm -r /var/volatile/tmp/*.tar > /dev/null 2>&1
echo "*****************************************"
echo "*                                       *"
echo "*   oZeta skin options installed        *"
echo "*****************************************"

exit 0
