# 같은 패키지(ex_1001) 안의 app.py에서 main 함수를 가져온다

from .app import main

# 이 패키지가 바깥에 공개하는 이름 목록
__all__ = ["main"]

# 프로젝트를 초기화 해준다
print("프로젝트 초기화 init")

