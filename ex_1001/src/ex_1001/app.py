#from .page86 import page86_ai_msg # . 이 메인함수와 같은 경로에 있다 from 파일명 import 파일 가보면 (***) 함수가 있다
#from .page95 import page95_user
from .page97 import page97_user

def sub():
    print("메인에서 실행하는 서브함수")




def main() -> None:  # init으로 넘어갈 일이 없다
    # print("메인화면 : app.py")
    # sub()
    # ai_msg = page86_ai_msg() # 컨트롤 마우스 클릭 -> 이동
    # print("~~~" + ai_msg + "여기는 app.py의 main()")
    #page86_ai_msg()
    # page95_user()

    page97_user()



# uv run ex-1001