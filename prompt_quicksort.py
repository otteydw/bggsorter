# Python program for implementation of Quicksort Sort

# partition and quicksort from https://www.geeksforgeeks.org/python-program-for-quicksort/

# This function takes last element as pivot, places
# the pivot element at its correct position in sorted
# array, and places all smaller (smaller than pivot)
# to left of pivot and all greater elements to right
# of pivot


def which_is_better(itemA, itemB):
    print("A: %s" % itemA)
    print("B: %s" % itemB)
    while True:
        choice = input("Which is better? ")
        if choice.lower() not in ('a', 'b'):
            print("Not an appropriate choice.")
        else:
            break
    print()
    if choice.lower() == 'a':
        return itemA
    else:
        return itemB


def partition(arr, low, high):
    i = (low-1)         # index of smaller element
    pivot = arr[high]     # pivot

    for j in range(low, high):

        # If current element is smaller than or
        # equal to pivot
        answer = which_is_better(arr[j], pivot)
        # if arr[j] <= pivot:
        if answer == pivot:

            # increment index of smaller element
            i = i+1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i+1], arr[high] = arr[high], arr[i+1]
    return (i+1)

# The main function that implements QuickSort
# arr[] --> Array to be sorted,
# low  --> Starting index,
# high  --> Ending index

# Function to do Quick sort


def quickSort(arr, low, high):
    if low < high:

        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(arr, low, high)

        # Separately sort elements before
        # partition and after partition
        quickSort(arr, low, pi-1)
        quickSort(arr, pi+1, high)


# Driver code to test above
# arr = [10, 7, 8, 9, 1, 5]
# arr = [19, 2, 31, 45, 6, 11, 121, 27]

# my_list = []
# my_list.append('A')
# my_list.append('B')
# my_list.append('C')
# my_list.append('E')
# my_list.append('D')


# n = len(arr)
# quickSort(arr, 0, n-1)
# print("Sorted array is:")
# print(arr)

# n = len(my_list)
# quickSort(my_list, 0, n-1)
# print("Sorted array is:")
# print(my_list)
