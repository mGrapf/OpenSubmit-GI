#! /bin/bash

PATH_AUFGABEN=*
PATH_RESULT="__Fertig"
#TEST_ASCII=True


if [ ! -d $PATH_RESULT ]; then
	mkdir $PATH_RESULT && echo "mkdir $PATH_RESULT"
fi

# jeden Ordner durchgehen
for D in *; do
    if [ -d "$D" ] && [ "$D" != "$PATH_RESULT" ]; then
    
		test -e "$D/validator_example.cpp" || continue
		printf "%-20s" "${D}"
		
		# Teste ob bereits gezippt
		if [ -e $PATH_RESULT"/validator_$D."* ] && [ -e $PATH_RESULT"/"$D"."* ]; then
			echo " -> skip"
			continue
		fi

		# Teste ASCII
		if [ $TEST_ASCII ]; then
			i=1
			while read line
			do
				if [[ $line = *[![:ascii:]]* ]]; then
					printf " -> validator_example.cpp: Non-Ascii\nline ${i}: ${line}\n"
					#exit 1
					continue
				fi
				((i=i+1))
			done < $D"/validator_example.cpp"
		fi
		
		# Führe Testscript aus
		if ! ./exec.sh $D >/dev/null ;then
			echo " -> Fehler"
			cat ./opensubmit-exec.log
			exit
		fi	
		
		
		# Packe main + example + validator (allgemein)
		#test -e "$D/validator.py" || ( zip -qjo "$PATH_RESULT/validator_$D.zip" validator.py $D/validator_example.cpp $D/validator_main.cpp || echo $D" -> ZIP-Fehler" )
		# Packe main + example + validator (aufgabenspezifisch)
		
		#test -e "$D/validator.py" && zip -qjo "$PATH_RESULT/validator_$D.zip" $D/validator.py $D/validator_example.cpp $D/validator_main.cpp && ( printf " -> spezifischer Validator" || echo " -> ZIP-Fehler" )

		echo " -> OK"
		
    fi
done
