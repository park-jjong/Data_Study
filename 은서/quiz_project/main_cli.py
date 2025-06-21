#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python OX 퀴즈 - CLI(Command Line Interface) 버전

이 프로그램은 터미널에서 실행되는 텍스트 기반 퀴즈 프로그램입니다.
CSV 파일에서 문제를 읽어와 사용자에게 O/X 퀴즈를 제공하고,
틀린 문제는 별도 파일로 저장하여 복습할 수 있습니다.
"""

# 필요한 모듈 임포트
from quiz_logic import load_questions, check_answer, save_wrong_questions, update_wrong_questions
import random  # 문제를 무작위로 섞기 위해 사용
import os      # 운영체제 관련 기능 (화면 지우기, 경로 처리 등)
import time    # 시간 지연을 위해 사용 (에러 메시지 표시 후 대기)

class QuizCLI:
    """
    CLI 기반 퀴즈 프로그램의 메인 클래스
    
    이 클래스는 퀴즈의 전체 흐름을 관리합니다:
    - 메뉴 표시 및 선택
    - 퀴즈 진행
    - 결과 표시 및 저장
    """
    
    def __init__(self):
        """
        클래스 초기화 메서드
        
        프로그램 시작 시 필요한 변수들을 초기화합니다.
        파일 경로를 설정하고 퀴즈 상태 변수들을 준비합니다.
        """
        # 파일 경로 설정
        # __file__: 현재 실행 중인 파일의 경로
        # abspath(): 절대 경로로 변환
        # dirname(): 디렉토리 경로만 추출
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 퀴즈 파일과 오답 파일의 전체 경로 생성
        # os.path.join(): 운영체제에 맞는 경로 구분자 사용
        self.quiz_file = os.path.join(current_dir, "ox_quiz_python.csv")
        self.wrong_file = os.path.join(current_dir, "wrong.csv")
        
        # 퀴즈 상태를 관리하는 변수들
        self.questions = []          # 문제 리스트 (딕셔너리의 리스트)
        self.current_index = 0       # 현재 문제 번호 (0부터 시작)
        self.score = 0              # 맞춘 문제 개수
        self.wrong_list = []        # 틀린 문제들을 저장할 리스트
        self.is_review_mode = False # 복습 모드 여부 (True: 복습, False: 일반)
        
    def clear_screen(self):
        """
        화면을 지우는 메서드
        
        운영체제에 따라 다른 명령어를 사용합니다:
        - Windows: cls
        - Linux/Mac: clear
        """
        # os.name이 'nt'면 Windows, 아니면 Unix 계열(Linux/Mac)
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """
        프로그램 헤더를 출력하는 메서드
        
        화면을 지우고 프로그램 제목을 보기 좋게 출력합니다.
        """
        self.clear_screen()
        print("=" * 50)  # 구분선 (50개의 = 출력)
        print("🧠 Python OX 퀴즈".center(50))  # 제목을 중앙 정렬
        print("=" * 50)
        print()  # 빈 줄 추가로 가독성 향상
    
    def start(self):
        """
        프로그램의 메인 루프
        
        사용자가 종료를 선택할 때까지 메뉴를 반복해서 표시합니다.
        """
        while True:  # 무한 루프 - break 명령으로만 종료
            self.print_header()
            
            # 메인 메뉴 출력
            print("1. 퀴즈 시작")
            print("2. 오답 복습")
            print("3. 종료")
            print()
            
            # 사용자 입력 받기
            # strip(): 앞뒤 공백 제거
            choice = input("선택하세요 (1-3): ").strip()
            
            # 선택에 따른 처리
            if choice == "1":
                self.start_normal_quiz()  # 일반 퀴즈 시작
            elif choice == "2":
                self.start_review_quiz()  # 오답 복습 시작
            elif choice == "3":
                print("\n프로그램을 종료합니다. 안녕히 가세요! 👋")
                break  # while 루프 종료
            else:
                # 잘못된 입력 처리
                print("\n❌ 잘못된 입력입니다. 다시 선택해주세요.")
                time.sleep(1)  # 1초 대기 (메시지를 읽을 시간 제공)
    
    def start_normal_quiz(self):
        """
        일반 퀴즈를 시작하는 메서드
        
        전체 문제를 불러와서 퀴즈를 진행합니다.
        """
        # CSV 파일에서 문제 불러오기
        self.questions = load_questions(self.quiz_file)
        
        # 파일이 없거나 비어있는 경우 처리
        if not self.questions:  # 빈 리스트는 False로 평가됨
            print(f"\n❌ {self.quiz_file} 파일을 찾을 수 없거나 비어있습니다!")
            input("\n계속하려면 Enter를 누르세요...")  # 사용자가 메시지를 읽을 시간 제공
            return  # 메서드 종료 (메인 메뉴로 돌아감)
        
        # 문제가 너무 적은 경우 경고
        if len(self.questions) < 3:
            # 사용자 확인 받기
            response = input(f"\n⚠️  문제가 {len(self.questions)}개밖에 없습니다. 계속하시겠습니까? (Y/N): ").strip().upper()
            if response != 'Y':
                return  # 사용자가 취소한 경우
        
        # 일반 모드로 설정하고 퀴즈 실행
        self.is_review_mode = False
        self.run_quiz()
    
    def start_review_quiz(self):
        """
        오답 복습을 시작하는 메서드
        
        이전에 틀린 문제들만 다시 풀어봅니다.
        """
        # 오답 파일에서 문제 불러오기
        self.questions = load_questions(self.wrong_file)
        
        # 복습할 문제가 없는 경우
        if not self.questions:
            print("\n📝 복습할 오답이 없습니다!")
            input("\n계속하려면 Enter를 누르세요...")
            return
        
        # 복습 모드로 설정하고 퀴즈 실행
        self.is_review_mode = True
        self.run_quiz()
    
    def run_quiz(self):
        """
        실제 퀴즈를 진행하는 메서드
        
        문제를 섞고, 하나씩 표시하며, 결과를 기록합니다.
        """
        # 퀴즈 상태 초기화
        self.current_index = 0  # 첫 번째 문제부터 시작
        self.score = 0          # 점수 초기화
        self.wrong_list = []    # 틀린 문제 리스트 초기화
        
        # 문제 순서를 무작위로 섞기
        # random.shuffle()은 리스트를 직접 수정함 (in-place)
        random.shuffle(self.questions)
        
        # 퀴즈 시작 화면
        self.print_header()
        mode_text = "🔁 복습 모드" if self.is_review_mode else "📖 일반 모드"
        print(f"{mode_text} - 총 {len(self.questions)}문제")
        print("\n💡 팁: 'Q'를 입력하면 퀴즈를 중단할 수 있습니다.")
        input("\n시작하려면 Enter를 누르세요...")
        
        # 문제 풀기 루프
        while self.current_index < len(self.questions):
            self.show_question()      # 현재 문제 표시
            if not self.get_answer(): # 답변 받기 (False 반환 시 중단)
                break
            self.current_index += 1   # 다음 문제로 이동
        
        # 퀴즈 종료 후 결과 표시
        self.show_results()
    
    def show_question(self):
        """
        현재 문제를 화면에 표시하는 메서드
        
        진행 상황과 함께 문제를 보기 좋게 출력합니다.
        """
        self.print_header()
        
        # 진행 상황 표시
        mode_text = "[복습 모드]" if self.is_review_mode else ""
        print(f"{mode_text} 문제 {self.current_index + 1} / {len(self.questions)}")
        print("-" * 50)  # 구분선
        
        # 현재 문제 가져오기
        question = self.questions[self.current_index]
        
        # 문제 출력
        # 딕셔너리에서 '질문' 키의 값을 가져옴
        print(f"\nQ{self.current_index + 1}. {question['질문']}")
        print()
    
    def get_answer(self):
        """
        사용자로부터 답변을 입력받고 처리하는 메서드
        
        Returns:
            bool: 계속 진행할지 여부 (True: 계속, False: 중단)
        """
        question = self.questions[self.current_index]
        
        while True:  # 올바른 입력을 받을 때까지 반복
            # 사용자 입력 받기
            answer = input("답을 입력하세요 (O/X, Q:종료): ").strip().upper()
            
            # 종료 명령 확인
            if answer in ['Q', 'QUIT']:
                # 정말 종료할지 재확인
                confirm = input("\n정말로 퀴즈를 그만하시겠습니까? (Y/N): ").strip().upper()
                if confirm == 'Y':
                    return False  # 퀴즈 중단
                continue  # 다시 답변 입력으로
            
            # 답변 체크 (quiz_logic의 함수 사용)
            is_correct = check_answer(answer, question['정답'])
            
            # 유효하지 않은 입력 처리
            if is_correct is None:
                print("❌ O 또는 X만 입력 가능합니다!")
                continue  # 다시 입력 받기
            
            # 결과 표시
            print()
            if is_correct:
                # 정답인 경우
                print("✅ 정답입니다!")
                self.score += 1  # 점수 증가
            else:
                # 오답인 경우
                print(f"❌ 오답입니다! 정답은 {question['정답']}입니다.")
                self.wrong_list.append(question)  # 틀린 문제 리스트에 추가
                
                # 해설 보기 옵션 제공
                show_explanation = input("\n해설을 보시겠습니까? (Y/N): ").strip().upper()
                if show_explanation == 'Y':
                    print(f"\n💡 해설: {question['해설']}")
            
            # 다음 문제로 넘어가기 전 대기
            input("\n다음 문제로 가려면 Enter를 누르세요...")
            return True  # 계속 진행
    
    def show_results(self):
        """
        퀴즈 결과를 표시하는 메서드
        
        점수, 정답률을 계산하고 틀린 문제를 저장합니다.
        """
        self.print_header()
        
        print("🎉 퀴즈 완료!")
        print("-" * 50)
        
        # 실제로 푼 문제 수 계산 (중간에 그만둔 경우를 위해)
        attempted = self.current_index
        if attempted == 0:
            print("문제를 풀지 않고 종료하셨습니다.")
            input("\n계속하려면 Enter를 누르세요...")
            return
        
        # 정답률 계산
        # 삼항 연산자 사용: 조건이 참이면 앞의 값, 거짓이면 뒤의 값
        accuracy = (self.score / attempted * 100) if attempted > 0 else 0
        
        # 결과 출력
        print(f"\n총 {attempted}문제 중 {self.score}문제 정답")
        print(f"정답률: {accuracy:.1f}%")  # .1f: 소수점 한 자리까지 표시
        
        # 모드에 따른 오답 처리
        if self.is_review_mode:
            # 복습 모드인 경우
            if self.wrong_list:
                # 아직도 틀린 문제가 있으면 업데이트
                update_wrong_questions(self.wrong_file, self.wrong_list)
                print(f"\n📝 아직 {len(self.wrong_list)}개의 문제를 더 복습해야 합니다.")
            else:
                # 모든 문제를 맞춘 경우 파일 삭제
                update_wrong_questions(self.wrong_file, [])  # 빈 리스트 전달 = 파일 삭제
                print("\n🎊 모든 오답을 정복했습니다!")
        else:
            # 일반 모드인 경우
            if self.wrong_list:
                # 틀린 문제가 있으면 저장
                save_wrong_questions(self.wrong_file, self.wrong_list)
                print(f"\n📁 틀린 문제 {len(self.wrong_list)}개가 저장되었습니다.")
        
        input("\n계속하려면 Enter를 누르세요...")

# 메인 실행 블록
# 이 파일이 직접 실행될 때만 실행됨 (import될 때는 실행 안 됨)
if __name__ == "__main__":
    try:
        # QuizCLI 인스턴스 생성 및 시작
        quiz = QuizCLI()
        quiz.start()
    except KeyboardInterrupt:
        # Ctrl+C로 프로그램을 중단한 경우
        print("\n\n프로그램이 중단되었습니다. 안녕히 가세요! 👋")
    except Exception as e:
        # 기타 예상치 못한 오류 발생 시
        print(f"\n오류가 발생했습니다: {e}")
        input("\n종료하려면 Enter를 누르세요...")