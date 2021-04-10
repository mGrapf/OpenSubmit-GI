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

Die Testmaschine kann als Docker-Image mit ``docker pull mGrapf/opensubmit-exec`` bezogen werden.

Eine Installation der aktuellsten Version ist mit ``pip install git+https://github.com/mgrapf/opensubmit#egg=opensubmit-exec\&subdirectory=executor`` möglich.

Ausführliche Anleitungen zur Installation und zur Testerstellung der C++ Testmaschine finden sich im `OpenSubmit-Wiki <https://github.com/mGrapf/opensubmit/wiki>`_ des Projekts.

