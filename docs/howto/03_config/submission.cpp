#include <iostream>
using namespace std;

int main()
{
	// Hinweis: operator ist ein keyword der Sprach C++ und damit als Variablenname nicht zulaessig
	float operand1, operand2;
	char op;
	
	cout << "Rechenaufgabe eingeben: " << endl;
	cout << "Operand 1: " << endl;
	cin >> operand1;
	cout << "Operator " << endl;
	cin >> op;
	cout << "Operand 2 " << endl;
	cin >> operand2;
	
	float erg;
	bool fehler = false; // Variable die angibt, ob ein Fehler aufgetreten ist
	
	switch(op)
	{
		case '+': erg = operand1 + operand2;
				  break;// fehlt break, wird der folgende Block ebenfalls ausgefuehrt
			
		case '*': erg = operand1 * operand2;
				  break;

		case '-': erg = operand1 - operand2;
				  break;
			
		case '/': if (operand2 != 0) // Divisiondurch 0 verhindern!
				  {
					  erg = operand1 / operand2;
				  }
				  else
				  {
					  cout << "Fehler: Division durch 0 " << endl;
					  fehler = true;
				  }
				  break;

		// Der default Block wird ausgefuehrt, wenn keiner der vorhergehenden Bloecke ausgefuehrt wurde
		default:
			cout << "Fehler: unbekannter Operator " << endl;
			fehler = true;
			break;
		
	}
	
	// wenn die Variable fehler immer noch auf false steht wurde das Ergebnis erfolgreich ausgerechnet
	if (!fehler)
	{
		cout << "Ergebnis: " << erg << endl;
	}
	
	return 0;
}
