#!/bin/sh

pyv="$(python -V 2>&1)"
echo "$pyv"
echo "Checking Dependencies"
echo ""
echo "updating feeds"
if [ -d /etc/opkg ]; then
    opkg update
    echo ""

    if [[ $pyv =~ "Python 3" ]]; then
        echo "checking python3-requests"
        if python -c "import requests" &> /dev/null; then
            echo "Requests library already installed"
        else
            echo "install python3-requests"
            opkg install python3-requests
        fi
        echo ""

    else
        echo "checking python-requests"
        if python -c "import requests" &> /dev/null; then
            echo "Requests library already installed"
        else
            echo "install python-requests"
            opkg install python-requests
        fi
        echo ""
    fi
fi
exit 0
