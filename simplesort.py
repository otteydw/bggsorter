#!/usr/bin/python3

def bubblesort(list):

    decisioncount=0
    for iter_num in range(len(list)-1,0,-1):
        for idx in range(iter_num):
            decisioncount+=1
            print ("A: %s" % list[idx])
            print ("B: %s" % list[idx+1])
            while True:
                choice = input(str(decisioncount) + ": Which is better? ")
                if choice.lower() not in ('a', 'b'):
                    print("Not an appropriate choice.")
                else:
                    break
            #if list[idx]>list[idx+1]:
            if choice.lower() == 'a':
                temp = list[idx]
                list[idx] = list[idx+1]
                list[idx+1] = temp
            print()

def insertion_sort(InputList):
    for i in range(1, len(InputList)):
        j = i-1
        nxt_element = InputList[i]
        # Compare the current element with next one
        while (InputList[j] > nxt_element) and (j >= 0):
            InputList[j+1] = InputList[j]
            j=j-1
        InputList[j+1] = nxt_element

list = [19,2,31,45,6,11,121,27]
bubblesort(list)
print(list)

my_list=[]

my_list.append('A')
my_list.append('B')
my_list.append('C')
my_list.append('E')
my_list.append('D')

print (my_list)
bubblesort(my_list)
print (my_list)
