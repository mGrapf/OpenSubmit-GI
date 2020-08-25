/* 
 * Implementieren Sie ein C++-Programm, welches den Inhalt eines Feldes
 * aufsteigend sortiert.
 * Entwerfen Sie dazu eine Funktion swap() und sort().
 */

#include <iostream>
using namespace std;

void swap(int &a, int &b){
	// ???
	// ???
	// ???
}

void sort (int *feld, int len){
	// ???
	// ???
	// ???
}

void print (int *array, int len){
	for (int i=0; i<len; i++)
		cout << array[i] << " ";
	cout << endl;
}

int main(){
	int feld[10] = {5,4,11,23,1,9,47,2,41,8};
	cout << "vor dem Sortieren: ";
	print(feld, 10);
	sort (feld, 10);
	cout << " nach dem Sortieren: ";
	print(feld,10);
	return 0;
}
