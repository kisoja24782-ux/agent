from typing import TypedDict


# 사용자
class User(TypedDict):
    id: int
    name: str
    email: str

def page95_user() -> User:
    user1: User = {
        'id' : 1,
        'name': 'kingsj',
        'email': 'hahahah@naver.com'
        }

    print(user1)
    
    return user1