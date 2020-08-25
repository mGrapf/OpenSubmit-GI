########################
OpenSubmit-Exec-Gi Howto
########################

1 Lokale Installation
---------------------
Da das Testen der erstellten Aufgaben durch  die OpenSubmit-Weboberfläche eher umständlich und langwierig ist, empfiehlt es sich den Validator zusätzlich auf dem eigenen Computer zu installieren. 

Über virtualenv
^^^^^^^^^^^^^^^

Um Ihre Python-Installation sauber zu halten, empfehlen wir die Verwendung von Virtualenv.

.. code-block:: sh

    sudo apt-get install python3-pip 
    sudo pip3 install virtualenv

    python3 -m venv ~/.opensubmit
    source ~/.opensubmit/bin/activate

    pip install --upgrade git+https://github.com/mgrapf/opensubmit-gi#egg=opensubmit-exec\&subdirectory=executor

    deactivate
    PATH=$PATH:~/opensubmit/bin

Oder direkt im System installieren:

.. code-block:: sh
    sudo apt-get install python3-pip
    pip install --upgrade git+https://github.com/mgrapf/opensubmit-gi#egg=opensubmit-exec\&subdirectory=executor


    
    
Sobald der Validator installiert ist kann er im Terminal mit „opensubmit-exec“ aufgerufen werden. Er erwartet mindestens einen weiteren Parameter. Wir interessieren uns allerdings zunächst allein auf den lokalen Validator-test: opensubmit-exec test <dir>

Wichtige Dateien
^^^^^^^^^^^^^^^^

    • validator_example.cpp
    • validator_main.cpp*
    • submission.cpp*
*Optional
    • validator.zip
    • submission.cpp

Da der C++-Validator die Abgabe immer mit einer Beispieldatei vergleicht, reicht es nicht ihn alleine zu speichern. Der Python-Validator muss immer mit mindestens einer cpp-Datei gepackt werden. In der aktuellen Version des C++-Validators werden vorgegebene Dateinamen verwendet (unterstrichen). Ein Validator-Zip sollte wie folgt aussehen:
    • einfacherTest.zip
        ◦ validator.py
        ◦ validator-example.cpp
Um einen Test zu beeinflussen, kann zusätzlich eine weitere cpp-Datei geschrieben werden, welche dann die validator-example.cpp aufruft. Ein solches Validator-Zip sollte so aussehen:
    • umfangreicherTest.zip
        ◦ validator.py
        ◦ validator-main.cpp
        ◦ validator-example.cpp


Validator starten
^^^^^^^^^^^^^^^^^
~/OS_Howto/02_validator_example/
Im ersten Ordner befindet sich ausschließlich die Datei
Beginnen wir mit einer einfachen Hello-World-Aufgabe. Schauen Sie sich den Ordner ~/OpenSubmitHowto/01_validator_example/ an. Dort befindet sich ein einfaches Hello-World-Programm mit dem Dateinamen validator_example.cpp.

Sie sollten sich in dem Ordner ~/OpenSubmitHowto/ befinden.
Geben Sie opensubmit-exec test 01_validator_example ein.
OpenSubmit startet nun und führt einen Test aus. Dabei überprüft nutzt er die Dateien in dem angegebenen Ordner.

Submission
^^^^^^^^^^
Um den Einstieg in OpenSubmit zu erleichtern werden wir hier den Ablauf der Erstellung von Tests Schritt für Schritt durchgehen. Wir gehen davon aus, dass der Executor bereits lokal auf Ihrem Computer installiert ist.
Wir fangen mit einem einfachen Hello-World-Programm an. Dazu benötigen wir eine Beispieldatei:

Es fällt auf, dass das Programm des Studenten von der Vorlage abweicht.
