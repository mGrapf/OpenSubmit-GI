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

    sudo apt-get install python3-venv 

    python3 -m venv ~/OpenSubmit 

    source OpenSubmit/bin/activate

    pip install opensubmit-exec

    deactivate

    PATH=$PATH:~/OpenSubmit/bin
    
Sobald der Validator installiert ist kann er im Terminal mit „opensubmit-exec“ aufgerufen werden. Er erwartet mindestens einen weiteren Parameter. Wir interessieren uns allerdings zunächst allein auf den lokalen Validator-test: opensubmit-exec test <dir>
