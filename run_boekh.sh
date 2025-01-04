#!/bin/bash

# Definieer de lijst met maanden
maanden=("januari" "februari" "maart" "april" "mei" "juni" "juli" "augustus" "september" "oktober" "november" "december")

# Reguliere expressie om te matchen op een maand
regex="^(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)$"

# Loop door de lijst van maanden
for maand in "${maanden[@]}"; do
    if [[ $maand =~ $regex ]]; then
        # Print de zin als de maand overeenkomt met de regex
        python3 main_read_boekh.py 2021 $maand
        echo "$maand  2021 is gedaan"
        echo $?
    fi
done

for maand in "${maanden[@]}"; do
    if [[ $maand =~ $regex ]]; then
        # Print de zin als de maand overeenkomt met de regex
        python3 main_read_boekh.py 2022 $maand
        echo "$maand  2022 is gedaan"
        echo $?
    fi
done

for maand in "${maanden[@]}"; do
    if [[ $maand =~ $regex ]]; then
        # Print de zin als de maand overeenkomt met de regex
        python3 main_read_boekh.py 2023 $maand
        echo "$maand  2023 is gedaan"
        echo $?
    fi
done



