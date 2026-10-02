day = 4
match day:
  case 1:
    print("Monday")
  case 2:
    print("Tuesday")
  case 3:
    print("Wednesday")
  case 4:
    print("Thursday")
    print("히히")
  case 5:
    print("Friday")
  case 6:
    print("Saturday")
  case 7:
    print("Sunday")


    '''
    히히 메롱
    '''
day = 6
match day:
  case 1 | 2 | 3 | 4 | 5:
    print("Today is a weekday")
  case 6 | 7:
    print("I love weekends!")

year = 5
holiday = 4
match holiday:
  case 1 | 2 | 3 | 4 | 5 if year == 4:
    print("A weekday in April")
  case 1 | 2 | 3 | 4 | 5 if year == 5:
    print("A weekday in May")
  case _:
    print("No match")