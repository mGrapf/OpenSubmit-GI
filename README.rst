OpenSubmit C++ Testmaschine
============================

`OpenSubmit <https://github.com/troeger/opensubmit>`_ besteht aus zwei Teilen: dem Webinterface und der Testmaschine, welche der Ausführung und dem Test der eingereichten Programme dient. Beide Teile können unabhängig voneinander arbeiten.

Dieser OpenSubmit-Fork behandelt ausschließlich die Testmaschine, welche für die Module "Grundlagen der Informatik I und II" der "TU Chemnitz" angepasst und erweitert wurde. Ziel war die Bedienung und Weiterentwicklung zu vereinfachen. Die Unterschiede zum Hauptprojekt können wie folgt zusammengefasst werden:

* Die Dokumentation wurde in deutscher Sprache verfasst.
* Projektdeien, welche nicht die Testmaschine betreffen, wurden entfernt.
* Die Testmaschine wurde u.a. um folgende Funktionen erweitert:
    * Automatischer Vergleich von C++ Programmen mit einer Mustervorlage
    * Erleichterte Bedienung des lokalen Tests
    * Sicherheitsfeatures: u.a. eine Programmausführung mit eingeschränktem Nutzerprofil

Für den Schnelleinstieg wurde ein Docker-Compose-Skript erstellt, welches automatisch den offiziellen OpenSubmit-Server, eine dafür notwendige Datenbank und die C++ Testmaschine herunterläd und ausführt. Führen Sie dazu folgende Schritte aus:

* ggf. `Docker <https://docs.docker.com/get-docker/>`_ und `Docker Compose <https://docs.docker.com/compose/install/>`_ installieren
* `docker-compose.yml <https://raw.githubusercontent.com/mGrapf/opensubmit/master/docker-compose.yml>`_ herunterladen
* Im Verzeichnis der docker-compose.yml ``docker compose up`` ausführen. Dies läd die erforderlichen Images herunter (ca. 2 GB) und startet diese mit einer Demo-Konfiguration.
* `http://localhost:8000 <http://localhost:8000>`_ aufrufen, um zur OpenSubmit Web-Oberfläche zu gelangen

Ausführliche Anleitungen zur Installation und Testerstellung finden sich im OpenSubmit-`Wiki <https://github.com/mGrapf/opensubmit/wiki>`_.

