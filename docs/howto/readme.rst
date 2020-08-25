########################
OpenSubmit-Exec-Gi Howto
########################

1 Lokale Installation
---------------------
Da das Testen der erstellten Aufgaben durch  die OpenSubmit-Weboberfläche eher umständlich und langwierig ist, empfiehlt es sich den Validator zusätzlich auf dem eigenen Computer zu installieren. Da Standardmäßig alle Python-Module in die allgemeine Systemumgebung installiert werden, empfielt es sich virtualenv zu nutzen. Dieses kann in separaten Verzeichnissen voneinander isolierte Python-Umgebungen erzeugen. Gerade um Programme zu testen empfielt sich diese Vorgehensweise, da so Versionskonflikte vermieden werden.

Die Anleitung beschreibt die Installation auf einem Debian-/Ubuntusystem im Heimatverzeichnis unter ".opensubmit".

Installation mit Virtualenv
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

    sudo apt-get install python3-pip python3-venv   # notwendige Packete installieren

    python3 -m venv ~/.opensubmit   # virtualenv-Pfad erzeugen - Der Pfad darf selbstverständlich variieren
    
    source ~/.opensubmit/bin/activate   # virtualenv aktivieren

    pip3 install --upgrade git+https://github.com/mgrapf/opensubmit-gi#egg=opensubmit-exec\&subdirectory=executor   # opensubmit installieren

    deactivate  # virtualenv wieder deaktivieren

Der OpenSubmit-Validator ist nun installiert. Um ihn aufzurufen muss wieder die virtuelle Umgebung wieder aktiviert werden. Alternativ gibt es volgende Möglichkeiten:

.. code-block:: sh

    # Variante 1: Programm mit vollständigem Pfad aufrufen
    ~/.opensubmit/bin/opensubmit-exe
    
    
    # Variante 2: Verzeichnis in PATH eintragen.
    # (Gilt nur für die aktuelle Sitzung)
    PATH=$PATH:~/.opensubmit/bin/
    opensubmit-exec
    
    
    # Vairante 3: Programmverzeichnis verknüpfen
    ln -s ~/.opensubmit/bin/opensubmit-exec ~/.local/bin
    opensubmit-exec

Variante 3 ist wäre eher für eine permanente Installation zu empfehlen. Alternativ kann ein OpenSubmit auch systemweit installiert werden:

.. code-block:: sh

    sudo apt-get install python3-pip python3-venv
    pip3 install --upgrade git+https://github.com/mgrapf/opensubmit-gi#egg=opensubmit-exec\&subdirectory=executor   # opensubmit installieren


Wichtige Dateien
^^^^^^^^^^^^^^^^
    
opensubmit-exec erwartet mindestens einen Parameter. Wir interessieren uns allerdings zunächst allein auf den lokalen Validator-test: opensubmit-exec test <dir>

    • validator_example.cpp
    • validator_main.cpp*
    • submission.cpp*
Optional
    • validator.zip
    • submission.cpp

Da der C++-Validator die Abgabe immer mit einer Beispieldatei vergleicht, reicht es nicht ihn alleine zu speichern. Der Python-Validator muss immer mit mindestens einer cpp-Datei gepackt werden. In der aktuellen Version des C++-Validators werden vorgegebene Dateinamen verwendet (unterstrichen). Ein Validator-Zip sollte wie folgt aussehen:
xxx


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
