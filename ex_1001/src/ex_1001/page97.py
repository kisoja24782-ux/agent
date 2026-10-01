from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str


def page97_user() -> User:
    user1: User ={
        'id' : 1,
        'name': 'kingkingSJ',
        'email': 'kingsj@gmail.com'
    }

    user1= User(**user1) # 딕셔너리 -> 검사된 User 객체
    print(user1)

    return user1