#include <iostream>
#include <string>
using namespace std;
int main()
{
    string A, B;
    cin>>A;
    cin>>B;
    double avg=0;
    for(int i=0;i<A.size();i++)
    {
        avg+=((A[i]+B[i])/2);
    }
    avg/=(int)A.size();
    cout<<avg;
}
