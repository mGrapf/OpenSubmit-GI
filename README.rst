OpenSubmit C++ Testmaschine
============================

Dies ist ein Fork der Testmaschine des `OpenSubmit-Projekts <https://github.com/troeger/opensubmit>`_.

Es beinhaltet folgende Schwerpunkte:

* Projekt durch die Reduzierung auf die Testmaschine verkleinern, um den Einstieg in OpenSubmit zu erleichtern
* Dokumentation und Anleitungen in deutscher Sprache
* Anpassungen für das "Modul Grundlagen Informatik I und II" der TU Chemnitz:

  * Integrierter C++ Vergleichstest
  * Erleichterte Bedienung des lokalen Tests
  * Mehr Sicherheit durch Non-Root-Modus

-------

Die Testmaschine kann als Docker-Image bezogen werden:

* ``docker pull mgrapf/opensubmit-exec``

Eine Installation mit Pip ist möglich durch:

* ``pip3 install`` `opensubmit_exec-0.9.9-py3-none-any.whl <https://github.com/mGrapf/opensubmit/raw/master/executor/dist/opensubmit_exec-0.9.9-py3-none-any.whl>`_

oder

* ``pip3 install git+https://github.com/mgrapf/opensubmit#egg=opensubmit-exec\&subdirectory=executor``


Ausführliche Anleitungen zur Installation und zur Testerstellung der C++ Testmaschine finden sich im `Wiki <https://github.com/mGrapf/opensubmit/wiki>`_.

---------

Für den Schnelleinstieg wurde ein Docker-Compose-Skript erstellt, welches automatisch den offiziellen OpenSubmit-Server, eine dafür notwendige Datenbank und die C++ Testmaschine herunterläd und ausführt. Führen Sie dazu folgende Schritte aus:

1. `Docker installieren <https://docs.docker.com/get-docker/>`_
2. `Docker Compose installieren <https://docs.docker.com/compose/install/>`_
3. Folgende Docker Compose Konfiguration herunterladen: `docker-compose.yml <https://raw.githubusercontent.com/mGrapf/opensubmit/master/docker-compose.yml>`_
4. ``docker-compose up`` im Terminal ausführen.
   Die docker-compose.yml muss sich dabei im aktuellen Verzeichnis befinden.
   Docker Compose läd nun automatisch die benötigten Docker Images herunter (ca. 2GB) und startet diese.
5. `http://localhost:8000/ <http://localhost:8000/>`_ aufrufen um zur OpenSubmit-Weboberfläche zu gelangen.



