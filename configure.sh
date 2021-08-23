#!/bin/bash
CRYPTOS="cryptos = ["
echo "Enter the cryptocurrency tickers you want to show separated by commas (ex: btc, eth, ada)"
IFS=',' read -r -a array
for index in "${!array[@]}"
do
    if (( $index != 0 )) ; then
    	CRYPTOS="${CRYPTOS}, "
    fi
    CRYPTOS="${CRYPTOS}\""
    CRYPTOS="${CRYPTOS}"${array[index]//[[:blank:]]/}
    CRYPTOS="${CRYPTOS}\""
done
CRYPTOS="${CRYPTOS}]"
sed -i "s/cryptos=.*/$CRYPTOS/g" /home/umbrel/umbrel-crypto-display/scripts/cryptoprice.py
echo "To see the new cryptocurrencies you need to restart the cryptoprice script. Do you want do do it now?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) bash stop.sh; bash start.sh; break;;
        No ) exit;;
    esac
done
