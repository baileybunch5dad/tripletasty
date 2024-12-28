add = lambda x, y: x + y
result = add(2, 3)
print(result)

numbers = [1, 2, 3, 4]
squared = list(map(lambda x: x**2, numbers))
print(squared)

numbers = [1,2,3,4,5]
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)

people = [('Alice', 25), ('Bob', 20), ('Charlie', 30)]
people.sort(key=lambda person: person[1]) # sort in place by second key
print(people)