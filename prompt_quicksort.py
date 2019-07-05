import pickle
import simplejson

# partition and quicksort modified from https://www.geeksforgeeks.org/python-program-for-quicksort/


def prompt(itemA, itemB):
    print("A: %s" % itemA)
    print("B: %s" % itemB)
    while True:
        choice = input("Which is better? ").lower()
        if choice.lower() not in ('a', 'b', 's'):
            print("Not an appropriate choice.")
        else:
            break
    print()
    if choice == 'a':
        return itemA
    return itemB


def partition(arr, low, high):
    i = (low-1)         # index of smaller element
    pivot = arr[high]     # pivot

    for j in range(low, high):

        # If current element is smaller than or
        # equal to pivot
        answer = prompt(arr[j], pivot)
        # if arr[j] <= pivot:
        if answer == pivot:

            # increment index of smaller element
            i = i+1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i+1], arr[high] = arr[high], arr[i+1]
    return (i+1)


def quickSort(arr, low=0, high=None):
    if high == None:
        high = len(arr)-1

    if low < high:

        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(arr, low, high)

        # Separately sort elements before
        # partition and after partition
        quickSort(arr, low, pi-1)
        quickSort(arr, pi+1, high)


# MAIN

with open('otteydw.txt') as loadfile:
    games = []
    for game in loadfile:
        games.append(game.rstrip('\n'))

quickSort(games)

with open('gamelist_sorted.json', 'w') as savefile:
    simplejson.dump(games, savefile)

for number, game in enumerate(games[::-1]):
    print(str(number+1) + ": " + game)
