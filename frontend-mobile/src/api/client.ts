import axios from 'axios'; // HTTP 통신을 위한 axios 라이브러리 임포트

// [중요] 모바일(Expo) 테스트 시 서버가 기동 중인 PC의 실제 IP를 사용해야 합니다.
const API_BASE_URL = 'http://136.111.211.8:8000/api/v1'; 

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // [보완 필요] 현재는 테스트용 토큰입니다. 실제 로그인 완료 후 SecureStore의 값을 주입해야 합니다.
    'Authorization': 'Bearer test-token', 
  },
});

// AI 분석 및 문제 생성 요청 함수
export const generateLearningContent = async (text: string) => {
  try {
    console.log('API 호출: 콘텐츠 생성 시작');
    // 백엔드 LearningRequest(text: str) 규격에 맞춰 전송
    const response = await apiClient.post('/learning/generate-content', { text });
    return response.data; // 서버에서 받은 퀴즈 데이터 반환
  } catch (error) {
    console.error('콘텐츠 생성 실패:', error);
    throw error;
  }
};

// 심화 논술 답안 평가 요청 함수
export const evaluateEssayAnswer = async (question: string, answer: string) => {
  try {
    console.log('API 호출: 논술 평가 요청');
    // 백엔드 EssayEvaluationRequest(question, answer) 규격에 맞춰 전송
    const response = await apiClient.post('/learning/evaluate-essay', { question, answer });
    return response.data; // AI의 상세 피드백 반환
  } catch (error) {
    console.error('논술 평가 실패:', error);
    throw error;
  }
};