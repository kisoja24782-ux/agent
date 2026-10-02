class Myclass:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# p1 = Myclass("KSJ", 20)
# print(p1.name, p1.age)


class Person:
    count = 0                 # 모든 객체가 공유

    def __init__(self, name):
        self.name = name
        Person.count += 1     # 객체가 만들어질 때마다 1 증가


# p1 = Person("Emil")
# p2 = Person("Tobias")
# print(Person.count)     


class Person1:
  def __init__(self, fname, lage):
    self.name = fname
    self.age = lage
  
  def printname(self):
      print(self.name, self.age)
    

#   def __str__(self):   # __str__ 은 객체 전체 p1을 문자열로 바꿀 때만 쓰임
#     return f"{self.name} ({self.age})"

# p1 = Person1("Tobias", 36)
# print(p1)



class Student(Person1):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)   # 이름 설정은 부모에게 맡기고  , Person1을 쓰면 self를 넣고 super() 를 쓰면 self빼야함
        self.graduationyear = year            # 학생만의 속성 추가


# x = Student("Mike", "Olsen", 2026)
# x.printname()              # Mike Olsen
# print(x.graduationyear)    # 2026



class Shape:
    def __init__(self, shape):
        self.shape = shape

    def outputprint(self):
        print(self.shape)


class Food:
    def __init__(self, food):
        self.food = food

    def foodprint(self):
        print(self.food)


class Information(Shape):
    def __init__(self, shape, color, area):
        super().__init__(shape)
        self.color = color
        self.area = area

    # print(S) 로 보고 싶으면 이거 쓰면 돼
    #def __str__(self):
    #    return f"모양: {self.shape}, 색: {self.color}, 넓이: {self.area}"

class Menu(Food):
    def __init__(self, food, cal, color, whowith):
        super().__init__(food)
        self.cal = cal
        self.color = color
        self.whowith = whowith

S = Information("원","빨강","55파이")
S.outputprint()
print(S.shape, S.color, S.area)


F = Menu( "라면", 4564 ,"빨강", "혼자")
F.foodprint()
print(F.food, F.cal, F.color, F.whowith)