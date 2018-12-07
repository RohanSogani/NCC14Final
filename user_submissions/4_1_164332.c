#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#define MAX 50


int main()
{
	char input[MAX];
	char outputCharacter[25];
	int sum = 0, i, j, temp=0;
	
	printf(" Enter the string---> ");
	fgets(input, MAX, stdin);			 			// Used for storing string containing spaces. Appends '\n' at the end, before '\0'.
	input[strlen(input) - 1] = '\0';				// Remove '\n'
	
	for(i = 0, j = 0; input[i] != '\0'; i++)
	{
		// Check if digit
		if(input[i] >= '0' && input[i] <= '9') {
			temp = (temp * 10) + input[i] - '0'	;
		}
		
		else {
			sum = sum + temp;						// Add number to total sum
			temp = 0;
			outputCharacter[j++] = input[i];		// Append to answer string
		}
	}
	if(temp != 0)
		sum = sum + temp;				// If there's a digit at the end, add to sum
	outputCharacter[j] = '\0';			// Add terminating NULL character
	printf(" Output characters--> %s\n Sum of digits--> %d\n",outputCharacter, sum);
	return 0;
}

