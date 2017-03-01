#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#define DEBUG_FAILURE_MODE

bool flip_coin(double prob)
{
  return (bool) ((random() / (double) RAND_MAX) <= prob);
}

inline unsigned int stuckAt(unsigned int data, int bit, int value)
{
    unsigned int oldData = data;

    data = (value==0) ? data & ( (1 << bit) ^ 0xFFFFFFFF) : data | (1 << bit);

    #ifdef DEBUG_FAILURE_MODE
	printf("stuckAt bit %d, value %d: before: %x, after: %x", bit, value, oldData, data);
	#endif

	return data;
}

unsigned int stuckHigh (unsigned int data, int bit)
{
	return stuckAt(data, bit, 1);
}

unsigned int stuckLow (unsigned int data, int bit)
{
	return stuckAt (data, bit, 0);
}

unsigned int bitFlip (unsigned int data, int bit)
{
    unsigned int oldData = data;

	data = data ^ (1 << bit);

	#ifdef DEBUG_FAILURE_MODE
	printf("bitFlip bit %d: before: %x, after: %x", bit, oldData, data);
	#endif

	return data;
}

unsigned int randomBitFlip (unsigned int data)
{
	int bit = rand() % 32;

	return bitFlip (data, bit);
}

