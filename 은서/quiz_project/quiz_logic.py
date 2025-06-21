import csv
import os

def load_questions(filepath):
    """
    CSV 파일에서 문제 목록을 불러와 리스트로 반환합니다.
    파일이 없거나 비어있을 경우 빈 리스트 반환
    """
    questions = []
    try:
        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(row)
    except FileNotFoundError:
        print(f"⚠️ 파일을 찾을 수 없습니다: {filepath}")
        return []
    except Exception as e:
        print(f"⚠️ 파일 읽기 오류: {e}")
        return []
    
    return questions

def check_answer(user_input, correct_answer):
    """
    사용자 입력이 정답과 일치하는지 대소문자 구분 없이 비교합니다.
    유효한 입력: O, X (대소문자 무관)
    """
    # 입력값 정리
    cleaned_input = user_input.strip().upper()
    
    # 유효성 검사
    if cleaned_input not in ['O', 'X']:
        return None  # 유효하지 않은 입력
    
    return cleaned_input == correct_answer.strip().upper()

def save_wrong_questions(filepath, wrong_list):
    """
    틀린 문제 리스트(wrong_list)를 CSV 파일로 저장합니다.
    """
    if not wrong_list:
        # 오답이 없으면 기존 파일 삭제
        if os.path.exists(filepath):
            os.remove(filepath)
        return

    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["질문", "정답", "해설"])
            writer.writeheader()
            writer.writerows(wrong_list)
    except Exception as e:
        print(f"⚠️ 파일 저장 오류: {e}")

def update_wrong_questions(filepath, remaining_wrong):
    """
    복습 모드에서 여전히 틀린 문제만 다시 저장
    모든 문제를 맞췄다면 파일 삭제
    """
    save_wrong_questions(filepath, remaining_wrong)