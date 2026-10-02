def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

# print(fahrenheit_to_celsius(77))
# print(fahrenheit_to_celsius(95))
# print(fahrenheit_to_celsius(50))


def my_function(num1):
  result = num1 + 100
  return result

# hihi = my_function(77)
# print(hihi)

def my_function2(fname, lname):
  # return을 안쓰면 None을 반환함
  return fname + " " + lname

# fullname = my_function2("길동", "홍")
# print(fullname)


def my_function3(country = "서울"):
  return print("나의 고향은 " + country)

# return 이 없으면 home1, home2, home3 에 None이 들어감
# home1 = my_function3("천안")
# home2 = my_function3()
# home3 = my_function3("광주")

def my_function4(animal, name):
  print("나의 애완동물", animal)
  print("나의 이름은", name)

my_function4(animal= "dog", name= "KingSJ")
