OpenSubmit
==========

Wohingegen andere Tools wie Moodle versuchen universell alle Arten von Aufgaben abzudecken, wurde OpenSubmit speziell für die Verwaltung und Kontrolle von Programmier-Aufgaben entwickelt.  Dadurch kann es die spezifischen Anforderungen an ein Programm-Validierungs-Tool erfüllen und gleichzeitig übersichtlich und leicht erlernbar sein.

OpenSubmit besteht aus zwei Teilen, dem Webinterface, welches der Verwaltung der einzelnen Einreichungen dient, und dem Programm-Validator. Beide Programme können unabhängig voneinander arbeiten. In diesem Dokument werden wir uns zunächst mit dem Validator beschäftigen, welcher in Zukunft nur noch OpenSubmit-Exec genannt wird.

1 OpenSubmit-Exec-GI
---------------------

„Das automatisierte Testen wird in OpenSubmit von einem Python 3-Skript durchgeführt, welches für jede Aufgabe neu erstellt werden muss. Was dieses Skript tut, ist Ihnen überlassen - am Ende benötigt OpenSubmit nur einen Hinweis auf das Ergebnis. Allgemeine Aufgaben wie das Kompilieren und Ausführen von Code werden von Hilfsfunktionen unterstützt, die Sie in diesem Skript verwenden können.“ [#FN1]_

OpenSubmit-Exec gibt dem Anwender also viel Freiheit, aber ggf. auch viel Arbeit. Gerade für den Einstieg in OpenSubmit und den Aufbau erster Aufgaben kann dies eine große Hürde darstellen. Da für die Lehrveranstaltungen Grundlagen der Informatik/Informatik I und II bereits die Programmiersprache auf C++ begrenzt ist und die Aufgaben überwiegend als Übung und somit ohne strenge Bewertung gegeben werden, kann die Aufgabe des Validators aber eingegrenzt werden.

Deshalb wurde, um das Erstellen von Aufgaben zu vereinfachen und zu beschleunigen, ein einzelnes und universell einsetzbares Validator-Skript geschrieben und in OpenSubmit-Exec integriert. Dieser kann den abgegebenem Beispielcode mit einer Beispieldatei vergleichen. Eine Aufgabe kann somit ohne spezifischem Python-Skript erstellt werden. Gerade für Tutoren ohne Python-Kenntnisse wird dadurch die Aufgabenerstellung stark erleichtert. Die Option der spezifische Aufgabenerstellung mit Validatorskript bleibt aber weiterhin gegeben.

Der neue Validator mit integriertem Vergleichsskript wurde für die Lehrveranstaltung Grundlagen Informatik entwickelt und wird entsprechend OpenSubmit-Exec-GI genannt. Das Erstellen von Aufgaben kann durch diesen stark vereinfacht werden. Allerdings gestaltet sich entsprechend auch die Bedienung etwas anders. Deshalb lohnt es sich einen Blick in das `Howto <https://github.com/mGrapf/opensubmit-gi/tree/master/docs/howto>`_ zu werfen.

2 OpenSubmit-Web-Gi
-------------------

kommt noch


Literatur
---------
.. [#FN1] http://docs.open-submit.org/en/latest/teacher.html#automated-testing-of-submissions
