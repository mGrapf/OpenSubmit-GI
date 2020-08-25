// [CONFIG]
// REMOVE_MAIN = TRUE
// TEST_CASE_1 = 5 5*R
// TEST_CASE_2 = 10 10*R
// TEST_CASE_3 = 20 20*R
// RANDOM_MIN = 0
// RANDOM_MAX = 30
// ;EOF
#include "validator_example.cpp"

int main(int argc, char* argv[]){
	int n;
	cin >> n;
	
	int feld[n];
	for(int i=0; i<n; i++)
		cin >> feld[i];
	
	cout << "Vor dem Sortieren: ";
	print(feld, n);
	
	cout << "Nach dem Sortieren: ";
	sort(feld, n);
	print(feld, n);
	return 0;
}
