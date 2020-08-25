########################
OpenSubmit-Exec-GI Howto
########################


Dieses Howto beschreibt die Nutzung des Validators der `OpenSubmit <https://github.com/troeger/opensubmit>`_-Modifikation `OpenSubmit-GI <https://github.com/mGrapf/opensubmit-gi>`_.

Bitte laden Sie sich dazu die Beispieldateien herunter und wechseln Sie in das entsprechende Verzeichnis.
Alle Dateien sind möglichst einfach gehalten, um die Verwendung des lokalen Validators leicht zu verstehen.

.. code-block:: sh
    
    git clone https://github.com/mGrapf/OpenSubmit-Exec-GI-Howto
    cd OpenSubmit-Exec-GI-Howto


Lokale Installation
-------------------
Da das Testen der erstellten Aufgaben durch  die OpenSubmit-Weboberfläche eher umständlich und langwierig ist, empfiehlt es sich den Validator zusätzlich auf dem eigenen Computer zu installieren. Da Standardmäßig alle Python-Module in die allgemeine Systemumgebung installiert werden, empfielt es sich virtualenv zu nutzen. Dieses kann in separaten Verzeichnissen voneinander isolierte Python-Umgebungen erzeugen um Versionskonflikte mit anderen Programmen zu verhindern. Gerade um OpenSubmit-GI zu testen empfielt sich diese Vorgehensweise, da das Validatorprogramm aus kompatibilitätsgründen den gleichen Namen wie die offizielle OpenSubmit-Version hat. 

Die Anleitung beschreibt die Installation auf einem Debian-/Ubuntusystem im Heimatverzeichnis unter ".opensubmit". Die Installationsumgebung kann selbstverständlich auch an anderen Orten erstellt werden.

.. code-block:: sh

    # notwendige Packete installieren
    sudo apt-get install python3-pip python3-venv

    # virtualenv-Pfad erzeugen
    python3 -m venv ~/.opensubmit
    
    # virtualenv aktivieren
    source ~/.opensubmit/bin/activate

    # opensubmit installieren
    pip3 install 01_install/*.whl

    # virtualenv wieder deaktivieren
    deactivate

Der OpenSubmit-Validator ist nun installiert. Um ihn aufzurufen muss wieder die virtuelle Umgebung wieder aktiviert werden. Alternativ gibt es volgende Möglichkeiten:

.. code-block:: sh

    # Variante 1: Programm mit vollständigem Pfad aufrufen
    ~/.opensubmit/bin/opensubmit-exe
    
    # Variante 2: Verzeichnis in PATH eintragen.
    # (Gilt nur für die aktuelle Sitzung)
    PATH=~/.opensubmit/bin/:$PATH
    opensubmit-exec
    
    # Vairante 3: Programmverzeichnis verknüpfen
    ln -s ~/.opensubmit/bin/opensubmit-exec ~/.local/bin
    opensubmit-exec

Variante 3 ist wäre eher für eine permanente Installation zu empfehlen. Alternativ kann ein OpenSubmit auch systemweit installiert werden:

.. code-block:: sh

    sudo apt-get install python3-pip python3-venv
    pip3 install --upgrade git+https://github.com/mgrapf/opensubmit-gi#egg=opensubmit-exec\&subdirectory=executor   # opensubmit installieren


Test 1 - Statische Ausgaben
-----------------------------
``opensubmit-exec test 02_example_submission``

Der lokale Test des Validators kann mit "opensubmit-exec test <dir>". Als Parameter muss diesem ein Verzeichnis mitgegeben werden, welches mindestens die Datei "validator_example.cpp" enthält. Im ersten Beispiel ist dies ein einfaches Hello-World-Programm. 
Theoretisch reicht dies dem Validator bereits. Wenn dieser keine Studentenabgabe "submission.cpp" im Verzeichnis findet, wird er alternativ die Ausgabe der Beispieldatei mit sich selbst vergleichen. 

.. code-block:: cpp

    #include <iostream>
    using namespace std;

    int main(int argc, char* argv[]){
        cout << "Hello World";
        return 0;
    }

Eine Studentenabgabe hat für den lokalen Test immer den Dateinamen "submission.cpp". Später auf dem Server ist der Dateiname aber bei einer einzelnen Datei egal.

.. code-block:: sh

    #include <iostream>
    using namespace std;

    int main(){
        cout << "Hello World!" << endl;
        return 0;
    }

Beim genauen hinsehen fallen allerdings kleine Unterschiede zur Beispieldatei auf: Ein "!" und ein Zeilenumbruch kamen in der Ausgabe hinzu. Der Validator wird in diesem Fall dennoch die Abgabe als richtig bewerten. Standardmäßig gibt die Beispielausgabe nur vor, welche Zeichen mindestens vorkommen müssen. Dies kann später aber für jede Aufgabe individuell festgelegt werden.

Probieren wir es aus:

.. code-block:: sh

    opensubmit-exec test 02_example_submission
    ...
    ...
    ...
    2020-08-25 22:46:07,523 (33): Sending result to OpenSubmit Server: [('SubmissionFileId', None), ('Message', 'All tests passed. Awesome!'), ('Action', None), ('MessageTutor', 'All tests passed.\nOutput:\n\nHello World'), ('ExecutorDir', '/tmp/42_s25_74u5/'), ('ErrorCode', 0), ('Secret', '49846zut93purfh977TTTiuhgalkjfnk89'), ('UUID', '66619473387506')]  
    
Wichtig ist am Ende der ErrorCode 0, bzw. die Nachricht ('Message', 'All tests passed. Awesome!'), welche später dem Studenten gezeigt wird.

Test 2 - Variable Eingaben/Ausgaben
--------------------------------------
``opensubmit-exec test 03_example_config``

Dieses Mal soll der Student einen einfachen Taschenrechner programmieren. Dazu befindet sich im Verzeichnis eine Datei "aufgabenstellung.cpp". Diese wird vom Validator ignoriert, kann aber für den Studenten hilfreich sein, da bereits Code-Schnipsel mit fertig formatierten Ausgaben enthalten sind. Für den Vergleichstest ist ausschließlich die submission.cpp und alle Dateien, die mit "validator\_" beginnen relevant.

In dieser Aufgabe wird keine statische Ausgabe verlangt. Um verschiedene Eingaben zu simulieren, können zu beginn des Beispiels in einer Konfiguration mehrere Test-Cases erstellt werden. Die Konfiguration ist im ini-Format, welche auskommentiert zu beginn der Vergleichsdatei erfolgen sollte. Die Eingaben sind durch Leerzeichen getrennt und werden dem Programm sowohl als Parameter, als auch als Konsoleneingabe mitgegeben.

.. code-block:: cpp

    // [CONFIG]
    // TEST_CASE_1 = 2 + 3
    // TEST_CASE_2 = 2 - 3.1
    // TEST_CASE_3 = 4.2 * 3.5
    // TEST_CASE_4 = -2 / 3
    // TEST_CASE_5 = 2 / 0
    // ;EOF
    #include <iostream>
    using namespace std;
    ...



Test 3 - Funktionen/Klassen
------------------------------
``opensubmit-exec test 04_example_validator_main``

Soll der Funktionen oder Klassen programmiert werden, so können diese auch unabhängig der vom Studenten abgegebenen main-Funktion getestet werden. Stattdessen können Sie eine weitere Datei anlegen, welche die main-Funktion und ggf. weiteren Code beinhaltet. Diese Datei heißt validator_main.cpp. Wird diese Datei verwendet, so muss auch die Konfiguration in dieser erfolgen. Die Möglichkeiten der Konfiguration werden im nächsten Kapitel behandelt.

Die Separate validator_main.cpp hat folgende vorteile:

* Separate main-Funktion (die main-Funktion der validator_example.cpp und der submission.cpp werden dann automatisch entfernt)
* Einheitliche Konsolenausgaben
* Separate Tests von Klassen und Funktionen
* Globale Elemente können bereits definiert werden
* etc.

.. code-block:: cpp

    // [CONFIG]
    // REMOVE_MAIN = TRUE
    // TEST_CASE_1 = 5 5*$RANDOM
    // TEST_CASE_2 = 10 10*$RANDOM
    // TEST_CASE_3 = 20 20*$RANDOM
    // RANDOM_MIN = 0
    // RANDOM_MAX = 30
    // ;EOF
    #include "validator_example.cpp"

    int main(int argc, char* argv[]){
        int n;
        cin >> n;
        ...
        ...
        ...

Der Validator wird zunächst die validator_main.cpp kompilieren und anschließend das #include "validator_example.cpp" mit der vom studenten abgegebenen Datei (submission.cpp) ersetzen und erneut kompilieren.


Konfigurationsmöglichkeiten der Validator-Tests
-----------------------------------------------
*Die Erklärungen der einzelnen Konfigurationen wird in Zukunft noch ergänzt.*


Test-Cases
^^^^^^^^^^
TEST_CASE_0 = 

...

TEST_CASE_5 = 

TEST_CASE_N =

N_TEST_CASES = 1

Zufällige Zahlen
^^^^^^^^^^^^^^^^
RANDOM_MIN = 0

RANDOM_MAX = 50

RANDOM_FLOAT = 0

Verbiete Rekursion
^^^^^^^^^^^^^^^^^^
RECURSION = FALSE

Erlaube weitere Bibliotheken
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ALLOW_LIBRARIES =

Strenger Vergleich
^^^^^^^^^^^^^^^^^^
COMPARE_ALL = FALSE

Ausgabe nacheinander testen
^^^^^^^^^^^^^^^^^^^^^^^^^^^
SEPARATOR = '\a'

Zusätzliche strengere Kompilierung
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
EXTRA_COMPILATION = 




