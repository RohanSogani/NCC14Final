#include<iostream>
#include<string>
#include<math.h>
using namespace std;

int main()
{
  long long r, b;
  cin >> r >> b;
  string ans;
  for(long long i = 0; i < r; ++i) {
    long long temp;
    cin >> temp;
    long long ones=0;
    while(temp){
      if(temp % 2 == 1)
	ones++;
      temp /= 2;
    }
    if(ones % 2 == 1)
      ans += '1';
    else
      ans += '0';
  }
  long long power=0, result = 0;
  cout << ans;
  for(string::reverse_iterator i = ans.rbegin(); i != ans.rend(); i++, power++){
    if(*i == '1')
      result += pow(2,power);
  }
  cout << result << endl;
  return 0;
}
