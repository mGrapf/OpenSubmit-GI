#include <iostream>
using namespace std;

void swap(int &a, int &b){
	int  t = a;
	a = b;
	b = t;
}

void sort(int *feld, int len){
	bool issort = false;
	int i;

	while (!issort){
		issort = true;
		for (i=0; i<len-1; i++){
			if (feld[i] > feld[i+1]){
				issort = false;
				swap(feld[i], feld[i+1]);
			}
		}
	}
}

void print(int *array, int len){
	for (int i=0; i<len; i++)
		cout << array[i] << " ";
	cout << endl;
}

int main(){
	int feld[10] = {5,4,11,23,1,9,47,2,41,8};
	cout << "Vor dem Sortieren: ";
	print(feld, 10);
	sort (feld, 10);
	cout << "Nach dem Sortieren: ";
	print(feld,10);
	return 0;
}
