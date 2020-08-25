// [CONFIG]
// TEST_CASE_1 = 2 + 3
// TEST_CASE_2 = 2 - 3.1
// TEST_CASE_3 = 4.2 * 3.5
// TEST_CASE_4 = -2 / 3
// TEST_CASE_5 = 2 / 0
// ;EOF
#include <iostream>
using namespace std;

int main(){
	float o1, o2;
	char op;
	cin >> o1 >> op >> o2;
	
	switch(op){
		case '+': cout << o1 + o2; break;
		case '*': cout << o1 * o2; break;
		case '-': cout << o1 - o2; break;
		case '/': if (o2 != 0)
				cout << o1 / o2;
			else
				cout << "Fehler"; break;
		default: cout << "Fehler"; break;
	}
	return 0;
}
